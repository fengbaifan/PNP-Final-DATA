from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_ID = "st-chp8-p239-note1-haskell-eight-month-maximum"
NEW_IDS = (
    "st-chp8-p239-note1-lcrespi-two-year-stay",
    "st-chp8-p239-note1-zanotti-multiple-florence-visits",
)
BACKUP_SUFFIX = "bak-s2-chp8-p239-note1-semantic-decomposition-20261015"
EXPECTED_HASHES = {
    "mentions.csv": "89d21be0a0e677d01414d206ebc5f51253a340a063e342eddbad78155f4cb000",
    "book-statements.jsonl": "3cfd275dd546b9432755164bbf1b746ea2b90ea04daa485946e019656fe13c16",
}
EXPECTED_SEGMENT_HASH = "62a4611253d2bf05494ef55b0511b53861b0947a05aee1c7a9fdbab976ecbc3f"
EXPECTED_AFTER = (430, 272, 54, 104)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return raw, list(reader.fieldnames or []), list(reader)


def append_rows(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"))
    writer.writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline
    return raw + stream.getvalue().encode("utf-8")


def is_open(row: dict[str, object]) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def endpoint_counts(rows: list[dict[str, object]]) -> tuple[int, int, int, int]:
    opens = [r for r in rows if is_open(r)]
    object_only = sum(bool(r.get("subject_candidate_id")) and not r.get("object_candidate_id") for r in opens)
    subject_only = sum(not r.get("subject_candidate_id") and bool(r.get("object_candidate_id")) for r in opens)
    both = sum(not r.get("subject_candidate_id") and not r.get("object_candidate_id") for r in opens)
    return len(opens), object_only, subject_only, both


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    mention_raw, mention_fields, mentions = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    for name, expected, actual in (
        ("mentions.csv", EXPECTED_HASHES["mentions.csv"], mention_raw),
        ("book-statements.jsonl", EXPECTED_HASHES["book-statements.jsonl"], statement_raw),
    ):
        if digest(actual) != expected:
            raise ValueError(f"Input table changed since review: {name}")

    segment = next(
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
        if json.loads(line).get("segment_id") == SEGMENT_ID
    )
    if segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError("Footnote segment changed")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    line_no = 449
    line = source_lines[line_no - 1]
    if not (line.startswith("1 L. Crespi, p. 211,") and "eight months at most" in line and "Zanotti, II, p. $4" in line):
        raise ValueError("Expected p.239 note 1 wording is missing")
    base_offset = sum(
        len(text) + 1
        for text in source_lines[int(segment["line_start"]) - 1 : line_no - 1]
    )
    line_base = base_offset
    # Exact spans are anchored to the unique p.239 note line; each mention is checked below.
    spans = {
        "he_two_year": (line.find("he was in Florence") + 0, line.find("he was in Florence") + 2),
        "florence": (line.find("Florence"), line.find("Florence") + len("Florence")),
        "he_eight_month": (line.find("1709 he was-there") + len("1709 "), line.find("1709 he was-there") + len("1709 he") ),
        "there_eight_month": (line.find("1709 he was-there") + len("1709 he was-"), line.find("1709 he was-there") + len("1709 he was-there")),
        "he_zanotti": (line.find("implies that he went there") + len("implies that "), line.find("implies that he went there") + len("implies that he")),
        "there_zanotti": (line.find("implies that he went there") + len("implies that he went "), line.find("implies that he went there") + len("implies that he went there")),
        "lcrespi_citation": (line.find("L. Crespi, p. 211"), line.find("L. Crespi, p. 211") + len("L. Crespi, p. 211")),
        "lcrespi_author": (line.find("L. Crespi"), line.find("L. Crespi") + len("L. Crespi")),
        "zanotti_citation": (line.find("Zanotti, II, p. $4"), line.find("Zanotti, II, p. $4") + len("Zanotti, II, p. $4")),
    }
    for key, (start, end) in spans.items():
        if start < 0 or end <= start:
            raise ValueError(f"Could not anchor source span: {key}")
    mention_rows = [
        ("m-chp8-p239-note1-artist-he-two-year", "cand-0871", "he", "he refers to Giuseppe Maria Crespi in Luigi Crespi's reported two-year account."),
        ("m-chp8-p239-note1-place-florence", "cand-3397", "Florence", "Explicit place named in the reported two-year account."),
        ("m-chp8-p239-note1-artist-he-eight-month", "cand-0871", "he", "The pronoun in the 1709 maximum-duration claim refers to Giuseppe Maria Crespi."),
        ("m-chp8-p239-note1-place-there-eight-month", "cand-3397", "there", "Anaphor in the 1709 claim refers to Florence."),
        ("m-chp8-p239-note1-artist-he-zanotti", "cand-0871", "he", "The pronoun in Haskell's summary of Zanotti refers to Giuseppe Maria Crespi."),
        ("m-chp8-p239-note1-place-there-zanotti", "cand-3397", "there", "Anaphor in Haskell's summary of Zanotti refers to Florence."),
        ("m-chp8-p239-note1-lcrespi-author-citation", "cand-7716", "L. Crespi", "Abbreviated author cited for the two-year account; kept distinct from painter Giuseppe Maria Crespi."),
        ("m-chp8-p239-note1-lcrespi-work-citation", "cand-6591", "L. Crespi, p. 211", "Short-form citation mapped to the bibliographically identified Vite de' Pittori bolognesi; cited page not independently read."),
        ("m-chp8-p239-note1-zanotti-work-citation", "cand-7115", "Zanotti, II, p. $4", "Short-form citation mapped to the existing Storia dell'Accademia Clementina record; printed page is 54."),
    ]
    offsets = {
        "m-chp8-p239-note1-artist-he-two-year": spans["he_two_year"],
        "m-chp8-p239-note1-place-florence": spans["florence"],
        "m-chp8-p239-note1-artist-he-eight-month": spans["he_eight_month"],
        "m-chp8-p239-note1-place-there-eight-month": spans["there_eight_month"],
        "m-chp8-p239-note1-artist-he-zanotti": spans["he_zanotti"],
        "m-chp8-p239-note1-place-there-zanotti": spans["there_zanotti"],
        "m-chp8-p239-note1-lcrespi-author-citation": spans["lcrespi_author"],
        "m-chp8-p239-note1-lcrespi-work-citation": spans["lcrespi_citation"],
        "m-chp8-p239-note1-zanotti-work-citation": spans["zanotti_citation"],
    }
    new_mentions = []
    for mid, cid, surface, note in mention_rows:
        start, end = offsets[mid]
        actual = line[start:end]
        if actual != surface:
            raise ValueError(f"Mention span mismatch for {mid}: {actual!r} != {surface!r}")
        new_mentions.append({
            "mention_id": mid,
            "segment_id": SEGMENT_ID,
            "candidate_id": cid,
            "surface_form": surface,
            "start_char": str(line_base + start),
            "end_char": str(line_base + end),
            "note": note,
        })
    existing_mention_ids = {m["mention_id"] for m in mentions}
    if any(m["mention_id"] in existing_mention_ids for m in new_mentions):
        raise ValueError("A new mention ID already exists")

    rows = [json.loads(text) for text in statement_raw.decode("utf-8").splitlines() if text.strip()]
    if endpoint_counts(rows) != (431, 272, 55, 104):
        raise ValueError(f"Unexpected pre-update endpoint counts: {endpoint_counts(rows)}")
    target = next((r for r in rows if r.get("statement_id") == TARGET_ID), None)
    if target is None or not is_open(target) or target.get("subject_candidate_id") is not None or target.get("object_candidate_id") != "cand-0871":
        raise ValueError("Expected open p.239 note 1 statement not found")
    if any(r.get("statement_id") in NEW_IDS for r in rows):
        raise ValueError("A new statement ID already exists")

    # Correct endpoint orientation: the reported subject is Crespi and Florence is the location.
    target["subject_candidate_id"] = "cand-0871"
    target["object_candidate_id"] = "cand-3397"
    target["original_quote"] = "whereas it has been shown that during - 1709 he was-there for eight months at most."
    tq = target["qualifiers"]
    tq["claim"] = "Haskell says Giuseppe Maria Crespi was in Florence during 1709 for at most eight months."
    tq["mentioned_candidate_ids"] = ["cand-0871", "cand-3397"]
    tq["cross_reference_statement_ids"] = list(dict.fromkeys(
        (tq.get("cross_reference_statement_ids") or []) + list(NEW_IDS)
    ))
    tq["relation_candidate_note"] = "Haskell's maximum-eight-month account is source-attributed and remains unreconciled with Luigi Crespi's two-year account and Haskell's reading of Zanotti; the cited works were not independently read."
    tq.pop("open_endpoint_reason", None)

    a_id, c_id = NEW_IDS
    common = {
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0871",
        "object_candidate_id": "cand-3397",
        "origin": "book",
        "source_file": segment["source_file"],
    }
    a_row = {
        **common,
        "statement_id": a_id,
        "predicate": "luigi_crespi_reported_giuseppe_maria_crespi_in_florence_for_two_years",
        "qualifiers": {
            "source_line_start": line_no, "source_line_end": line_no,
            "printed_page": 239, "pdf_physical_page": 45,
            "claim": "Haskell reports that the account cited as L. Crespi, p. 211 says Giuseppe Maria Crespi was in Florence for two years.",
            "speaker": "Haskell", "quoted_speaker": "Luigi Crespi",
            "text_layer": "footnote report",
            "qualification": "This is Haskell's report of Luigi Crespi's account; the cited page was not independently read. Haskell gives a different maximum for 1709 in a separate statement.",
            "mentioned_candidate_ids": ["cand-0871", "cand-3397", "cand-7716", "cand-6591"],
            "attributed_source_candidate_ids": ["cand-6591"],
            "footnote_marker": 1,
            "relation_candidate": True,
            "relation_candidate_note": "The source reports an attributed two-year stay; preserve Luigi Crespi's attribution and do not treat the duration as independently verified.",
            "cross_reference_statement_ids": [TARGET_ID],
        },
        "original_quote": "L. Crespi, p. 211, says that he was in Florence for two years",
    }
    c_row = {
        **common,
        "statement_id": c_id,
        "predicate": "zanotti_implies_giuseppe_maria_crespi_visited_florence_several_times",
        "qualifiers": {
            "source_line_start": line_no, "source_line_end": line_no,
            "printed_page": 239, "pdf_physical_page": 45,
            "claim": "Haskell says Zanotti, volume II, page 54 implies that Giuseppe Maria Crespi went to Florence several times.",
            "speaker": "Haskell",
            "text_layer": "footnote report",
            "qualification": "This is Haskell's inference from the cited passage in Zanotti; the source was not independently read, and the wording does not establish the dates or number of visits.",
            "mentioned_candidate_ids": ["cand-0871", "cand-3397", "cand-7115"],
            "attributed_source_candidate_ids": ["cand-7115"],
            "footnote_marker": 1,
            "relation_candidate": True,
            "relation_candidate_note": "Keep Haskell's 'implies' qualification; do not convert the cited source's implication into a verified itinerary.",
            "cross_reference_statement_ids": [TARGET_ID, a_id],
            "ocr_corrections": [{"source_line": line_no, "ocr": "p. $4", "print": "p. 54", "basis": "CHP-8.pdf physical page 45"}],
        },
        "original_quote": "On the other hand Zanotti, II, p. $4, implies that he went there several times.",
    }
    rows.extend([a_row, c_row])
    if endpoint_counts(rows) != EXPECTED_AFTER:
        raise ValueError(f"Unexpected post-update endpoint counts: {endpoint_counts(rows)}")

    mention_after = append_rows(mention_raw, mention_fields, new_mentions)
    statement_after = ("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows)).encode("utf-8")
    print(f"mentions={len(mentions)}->{len(mentions) + len(new_mentions)}")
    print(f"statements={len([1 for x in statement_raw.decode('utf-8').splitlines() if x.strip()])}->{len(rows)}")
    print("updated_endpoint=st-chp8-p239-note1-haskell-eight-month-maximum|cand-0871->cand-3397")
    print(f"added_statements={a_id},{c_id}")
    print(f"open_endpoints={endpoint_counts([json.loads(x) for x in statement_raw.decode('utf-8').splitlines() if x.strip()])}->{endpoint_counts(rows)}")
    for name, before, after in (("mentions.csv", mention_raw, mention_after), ("book-statements.jsonl", statement_raw, statement_after)):
        print(f"{name} sha256 {digest(before)}->{digest(after)}")
    if args.preview:
        return 0

    outputs = ((MENTIONS, mention_after), (STATEMENTS, statement_after))
    pairs: list[tuple[Path, Path, Path, bytes]] = []
    for path, data in outputs:
        backup = path.with_name(f"{path.name}.{BACKUP_SUFFIX}")
        temp = path.with_name(f"{path.name}.tmp-{BACKUP_SUFFIX}")
        if backup.exists() or temp.exists():
            raise FileExistsError(f"Recovery or temporary file already exists: {path.name}")
        pairs.append((path, backup, temp, data))
    for path, backup, _, _ in pairs:
        shutil.copy2(path, backup)
    replaced: list[tuple[Path, Path]] = []
    try:
        for _, _, temp, data in pairs:
            temp.write_bytes(data)
        for path, backup, temp, _ in pairs:
            temp.replace(path)
            replaced.append((path, backup))
    except Exception:
        for _, _, temp, _ in pairs:
            if temp.exists():
                temp.unlink()
        for path, backup in replaced:
            shutil.copy2(backup, path)
        raise
    for path, backup, _, _ in pairs:
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.relative_to(ROOT)}:{digest(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
