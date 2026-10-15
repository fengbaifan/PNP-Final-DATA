from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources/02-Markdown/05_CHP-5_sec_i.md"
PDF = ROOT / "02-sources/01-book/CHP-5.pdf"
SEGMENT_ID = "chp-5:05_CHP-5_sec_i:l9-15"
SEGMENT_SHA256 = "d038ae7e4e778a83837f2cc9532e73b7cf65f14dd69ef72ec7f9269435a50144"
SOURCE_SHA256 = "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee"
PDF_SHA256 = "f63dca79808fde73ba10aa9414fef89bc8ca5e77ed829b2d5c86f23719e0674a"
TABLES = {
    "statements": ROOT / "04-knowledge/tables/book-statements.jsonl",
    "candidates": ROOT / "04-knowledge/tables/entity-candidates.csv",
    "mentions": ROOT / "04-knowledge/tables/mentions.csv",
    "coverage": ROOT / "04-knowledge/tables/s2-coverage.csv",
}
EXPECTED_SHA256 = {
    "statements": "68763c00006e0d8098da339e55760507966158ad7ed7f599381095c9d9a600e9",
    "candidates": "e14f9470b686431c8bcee8e688ff763f3230c6bcd6077dcf39e7439dae06540a",
    "mentions": "e9a05482d8a6cf238726abbcfbfa8779c11a4b214d090250855e7974ba9947dc",
    "coverage": "1211ffbc9d99f39ee53b132b2585d316452384efa7577fc904e63b8e2775b260",
}
BACKUP_SUFFIX = ".bak-s2-chp5-p121-20261011"
NEW_STATEMENT_ID = "st-chp5-p121-accademia-members-ban-dealing"
NEW_CANDIDATE_ID = "cand-11691"
NEW_MENTION_ID = "m-chp5-p121-s2-accademia-members"
RELATION_NOTE = (
    "S2 source-attributed relation candidate only; this classification does not create a formal S6 edge."
)
ORIGINALS = {
    "st-chp5-p121-accademia-complaint": ("cand-3470", "institutional_complaint_reported", "cand-0125"),
    "st-chp5-p121-accademia-ban-tax": ("cand-3470", "institutional_rule_and_tax_reported", "cand-0125"),
    "st-chp5-p121-dealer-trade-population": ("cand-0125", "dealer_practices_and_population_reported", "cand-3455"),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    return raw, bom, text, list(csv.DictReader(io.StringIO(text, newline="")))


def emit_csv(headers, rows, bom: bool, original_text: str) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=headers,
        lineterminator="\r\n" if "\r\n" in original_text else "\n",
        extrasaction="raise",
    )
    writer.writeheader()
    writer.writerows(rows)
    raw = stream.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" if bom else b"") + raw


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify the p.121 Accademia and dealer statements with guarded writes.")
    parser.add_argument("--apply", action="store_true", help="write the reviewed update and preserve backups")
    args = parser.parse_args()

    if digest(SOURCE.read_bytes()) != SOURCE_SHA256 or digest(PDF.read_bytes()) != PDF_SHA256:
        raise SystemExit("STOP: source or CHP-5 PDF changed")
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment = "\n".join(source_lines[8:15])
    if digest(segment.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("STOP: canonical p.121 source segment changed")
    required = (
        "so complained the Accademia di S.\nLuca.",
        "For these reasons it forbade its own members to engage in dealing on pain of expulsion.3",
        "in 1633 it managed to get papal authority to impose a special tax of ten scudi a year on all art dealers.",
        "As might be expected this caused a good deal of trouble, and ensuing controversies give us some insight into the situation.4",
        "in 1674 there were at least a hundred, most of them installed around the Piazza Navona.",
    )
    for quote in required:
        if quote not in segment:
            raise SystemExit(f"STOP: expected p.121 source quote missing: {quote!r}")

    raw = {name: path.read_bytes() for name, path in TABLES.items()}
    for name, data in raw.items():
        if digest(data) != EXPECTED_SHA256[name]:
            raise SystemExit(f"STOP: {name} table SHA changed: {digest(data)}")
    statements = [json.loads(line) for line in raw["statements"].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("STOP: duplicate statement IDs")
    for statement_id, expected in ORIGINALS.items():
        row = by_id.get(statement_id)
        if row is None:
            raise SystemExit(f"STOP: expected statement missing: {statement_id}")
        actual = (row.get("subject_candidate_id"), row.get("predicate"), row.get("object_candidate_id"))
        if actual != expected or "relation_candidate" in (row.get("qualifiers") or {}):
            raise SystemExit(f"STOP: original statement changed or already classified: {statement_id}: {actual}")
    if NEW_STATEMENT_ID in by_id:
        raise SystemExit("STOP: planned new statement ID already exists")

    candidate_raw, candidate_bom, candidate_text, candidates = read_csv(TABLES["candidates"])
    candidate_ids = {row["candidate_id"] for row in candidates}
    if len(candidate_ids) != len(candidates) or NEW_CANDIDATE_ID in candidate_ids:
        raise SystemExit("STOP: candidate ID collision")
    if max(int(cid.removeprefix("cand-")) for cid in candidate_ids) != 11690:
        raise SystemExit("STOP: candidate ID counter changed")

    mention_raw, mention_bom, mention_text, mentions = read_csv(TABLES["mentions"])
    mention_ids = {row["mention_id"] for row in mentions}
    if len(mention_ids) != len(mentions) or NEW_MENTION_ID in mention_ids:
        raise SystemExit("STOP: mention ID collision")
    mention_by_id = {row["mention_id"]: row for row in mentions}

    coverage = read_csv(TABLES["coverage"])[3]
    rows = [row for row in coverage if row["segment_id"] == SEGMENT_ID]
    if len(rows) != 1 or rows[0]["disposition"] != "reviewed" or rows[0]["migration_status"] != "complete":
        raise SystemExit("STOP: p.121 segment is not reviewed/complete")

    start = segment.find("its own members")
    if start < 0 or segment.find("its own members", start + 1) >= 0:
        raise SystemExit("STOP: p.121 Accademia membership phrase is missing or ambiguous")
    new_mention = {
        "mention_id": NEW_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": NEW_CANDIDATE_ID,
        "surface_form": "its own members",
        "start_char": str(start),
        "end_char": str(start + len("its own members")),
        "note": "Accademia di S. Luca members subject to the reported prohibition; individual membership is unspecified.",
    }

    candidate = {
        "candidate_id": NEW_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Members of Accademia di S. Luca described on p.121 (membership unspecified)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says the Accademia forbade its own members from dealing on pain of expulsion. The text identifies no members or individual cases.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L13",
    }
    if candidate["canonical_name"].casefold() in {row["canonical_name"].casefold() for row in candidates}:
        raise SystemExit("STOP: duplicate Accademia-member candidate label")

    # The p.121 footnote 3 citation supports the members’ prohibition; note 4 supports the tax dispute.
    tax_row = by_id["st-chp5-p121-accademia-ban-tax"]
    tax_row["predicate"] = "secured_authority_to_impose_tax_on"
    tax_row["original_quote"] = (
        "But the Accademia was ever on the lookout for new sources of income, and in 1633 it managed to get papal authority to impose a special tax of ten scudi a year on all art dealers. As might be expected this caused a good deal of trouble, and ensuing controversies give us some insight into the situation.4"
    )
    tax_q = tax_row.setdefault("qualifiers", {})
    tax_q.update(
        {
            "claim": "Haskell says the Accademia obtained papal authority in 1633 to impose a special tax of ten scudi a year on all art dealers; the measure caused controversy.",
            "qualification": "Source-reported institutional action; no pope or papal officeholder is identified. The annual rate and date are Haskell’s statements.",
            "relation_candidate": True,
            "relation_candidate_note": RELATION_NOTE,
            "mentioned_candidate_ids": ["cand-0125", "cand-3470"],
            "source_line_start": 13,
            "source_line_end": 13,
            "footnote_numbers": [4],
            "footnote_links": [link for link in tax_q.get("footnote_links", []) if link.get("marker") == 4],
            "footnote_link_status": "linked",
            "tax_amount": "ten scudi per year",
            "tax_authority": "papal authority; authority-holder unidentified",
            "date": 1633,
        }
    )

    complaint = by_id["st-chp5-p121-accademia-complaint"]
    complaint_q = complaint.setdefault("qualifiers", {})
    complaint_q["relation_candidate"] = True
    complaint_q["relation_candidate_note"] = (
        "The quoted Accademia complaint explicitly concerns dealers’ practice of offering sacred and palace works for sale like cheap goods; this remains a source-attributed S2 candidate."
    )

    population = by_id["st-chp5-p121-dealer-trade-population"]
    population_q = population.setdefault("qualifiers", {})
    population_q["relation_candidate"] = True
    population_q["relation_candidate_note"] = (
        "The statement explicitly places most of the reported dealer population around Piazza Navona in 1674; its other practice and population details remain Haskell’s source claims."
    )

    n3 = by_id["st-chp5-note-p121-n3-citation"]
    n3_q = n3.setdefault("qualifiers", {})
    n3_q["linked_body_statement_ids"] = [NEW_STATEMENT_ID]
    marker3 = next(
        link for link in by_id["st-chp5-p121-accademia-ban-tax"]["qualifiers"]["footnote_links"]
        if link.get("marker") == 3
    ) if any(link.get("marker") == 3 for link in by_id["st-chp5-p121-accademia-ban-tax"]["qualifiers"]["footnote_links"]) else {
        "marker": 3,
        "note_line": 128,
        "note_segment": "chp-5:05_CHP-5_sec_i:l125-147",
        "note_statement_ids": ["st-chp5-note-p121-n3-citation"],
        "status": "linked",
    }

    new_statement = {
        "statement_id": NEW_STATEMENT_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-3470",
        "object_candidate_id": NEW_CANDIDATE_ID,
        "predicate": "forbade_members_to_engage_in_dealing",
        "qualifiers": {
            "source_line_start": 13,
            "source_line_end": 13,
            "pdf_physical_page": 2,
            "printed_page_locator": "p.121",
            "claim": "Haskell says the Accademia forbade its own members to engage in dealing on pain of expulsion.",
            "speaker": "Haskell",
            "text_layer": "authorial narration",
            "qualification": "Reported institutional rule; no individual member or instance of enforcement is named.",
            "mentioned_candidate_ids": ["cand-3470", NEW_CANDIDATE_ID],
            "relation_candidate": True,
            "relation_candidate_note": RELATION_NOTE,
            "footnote_numbers": [3],
            "footnote_links": [marker3],
            "footnote_link_status": "linked",
        },
        "original_quote": "For these reasons it forbade its own members to engage in dealing on pain of expulsion.3",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
    }
    if new_statement["original_quote"] not in segment:
        raise SystemExit("STOP: new Accademia rule quote does not match source")

    for statement_id in ORIGINALS:
        row = by_id[statement_id]
        row.setdefault("qualifiers", {})["relation_candidate"] = True
        if statement_id != "st-chp5-p121-accademia-ban-tax":
            row["qualifiers"]["relation_candidate_note"] = (
                "S2 source-attributed relation candidate only; this classification does not create a formal S6 edge."
            )
    if NEW_CANDIDATE_ID not in {row["candidate_id"] for row in candidates}:
        candidates.append(candidate)
    mentions.append(new_mention)
    all_candidate_ids = candidate_ids | {NEW_CANDIDATE_ID}
    for row in [by_id[sid] for sid in ORIGINALS] + [new_statement]:
        if not row.get("subject_candidate_id") or not row.get("object_candidate_id"):
            raise SystemExit(f"STOP: classified p.121 relation lacks two endpoints: {row['statement_id']}")
        if row["subject_candidate_id"] not in all_candidate_ids or row["object_candidate_id"] not in all_candidate_ids:
            raise SystemExit(f"STOP: unknown p.121 endpoint: {row['statement_id']}")
        if not {row["subject_candidate_id"], row["object_candidate_id"]}.issubset(set(row["qualifiers"]["mentioned_candidate_ids"])):
            raise SystemExit(f"STOP: endpoint absent from mentioned_candidate_ids: {row['statement_id']}")

    has_bom = raw["statements"].startswith(b"\xef\xbb\xbf")
    text = raw["statements"].decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    out_lines = []
    for raw_line in text.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        ending = raw_line[len(line):]
        if not line.strip():
            out_lines.append(raw_line)
            continue
        row = json.loads(line)
        if row["statement_id"] in by_id:
            row = by_id[row["statement_id"]]
            line = json.dumps(row, ensure_ascii=False)
            ending = ending or newline
        out_lines.append(line + ending)
    if out_lines and not out_lines[-1].endswith(("\n", "\r")):
        out_lines[-1] += newline
    out_lines.append(json.dumps(new_statement, ensure_ascii=False) + newline)
    statement_bytes = (b"\xef\xbb\xbf" if has_bom else b"") + "".join(out_lines).encode("utf-8")

    candidate_bytes = emit_csv(list(candidates[0].keys()), candidates, candidate_bom, candidate_text)
    mention_bytes = emit_csv(list(mentions[0].keys()), mentions, mention_bom, mention_text)
    output = {"statements": statement_bytes, "candidates": candidate_bytes, "mentions": mention_bytes}
    print("p.121 existing dual-endpoint statements classified: 3")
    print("p.121 new relation statement: 1 (Accademia members’ prohibition)")
    print("new candidate: 1 (unnamed Accademia membership group); new mention: 1")
    print("citations: marker 3 linked to the prohibition; marker 4 retained on the tax statement")
    for sid in (*ORIGINALS.keys(), NEW_STATEMENT_ID):
        row = by_id.get(sid, new_statement)
        print(f"  {sid}: {row['subject_candidate_id']} -> {row['object_candidate_id']}; {row['predicate']}")
    if not args.apply:
        print("dry-run only; no files written")
        return 0

    paths = {name: TABLES[name] for name in output}
    backups = {name: path.with_name(path.name + BACKUP_SUFFIX) for name, path in paths.items()}
    for name, backup in backups.items():
        if backup.exists():
            raise SystemExit(f"STOP: recovery copy already exists: {backup.name}")
        shutil.copy2(paths[name], backup)
    written = []
    try:
        for name, data in output.items():
            temp = paths[name].with_name(paths[name].name + ".tmp-s2-chp5-p121")
            temp.write_bytes(data)
            temp.replace(paths[name])
            written.append(name)
    except Exception:
        for name in written:
            shutil.copy2(backups[name], paths[name])
        raise
    for name, path in paths.items():
        print(f"{name}: {digest(path.read_bytes())}; recovery copy {backups[name].name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
