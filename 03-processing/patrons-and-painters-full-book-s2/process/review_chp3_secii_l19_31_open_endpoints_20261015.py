from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
SUFFIX = "bak-s2-chp3-secii-l19-31-open-endpoints-20261015"
SEGMENT_ID = "chp-3:03_CHP-3_sec_ii:l19-31"
NEW_STATEMENT_ID = "st-chp3-secii-l19-31-stefano-torture-explanations-attached"
NOTE2_LINK_IDS = {
    "st-chp3-secii-p67-note2-necrology",
    "st-chp3-secii-p67-note2-necrology-claim",
}

ID_START = 12308
MENTION_START = 37


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return raw, list(reader.fieldnames or []), list(reader)


def append_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    if not rows:
        return raw
    newline = "\r\n" if b"\r\n" in raw else "\n"
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=fields, lineterminator=newline, extrasaction="raise")
    writer.writerows(rows)
    suffix = buf.getvalue().encode("utf-8")
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline.encode("ascii")
    return raw + suffix


def open_count(raw: bytes) -> int:
    total = 0
    for line in raw.decode("utf-8").splitlines():
        item = json.loads(line)
        q = item.get("qualifiers") or {}
        if q.get("relation_candidate") is True and (
            not item.get("subject_candidate_id") or not item.get("object_candidate_id")
        ):
            total += 1
    return total


def next_ids(candidate_rows: list[dict[str, str]], mention_rows: list[dict[str, str]]) -> tuple[list[str], list[str]]:
    numbers = [int(m.group(1)) for r in candidate_rows if (m := re.fullmatch(r"cand-(\d+)", r["candidate_id"]))]
    max_candidate = max(numbers, default=0)
    if max_candidate != ID_START - 1:
        raise ValueError(f"Candidate sequence changed: expected max {ID_START - 1}, got {max_candidate}")
    existing_mentions = {r["mention_id"] for r in mention_rows}
    numeric_suffixes = [
        int(m.group(1))
        for r in mention_rows
        if r.get("segment_id") == SEGMENT_ID
        and (m := re.fullmatch(r"m-chp3-secii-l19-31-(\d+)", r["mention_id"]))
    ]
    max_mention = max(numeric_suffixes, default=0)
    if max_mention != MENTION_START - 1:
        raise ValueError(f"Mention sequence changed: expected max {MENTION_START - 1}, got {max_mention}")
    candidate_ids = [f"cand-{n}" for n in range(ID_START, ID_START + 6)]
    mention_ids = [f"m-chp3-secii-l19-31-{n:04d}" for n in range(MENTION_START, MENTION_START + 7)]
    if existing_mentions.intersection(mention_ids):
        raise ValueError("One or more planned mention IDs already exist")
    return candidate_ids, mention_ids


def segment_text() -> str:
    for line in SEGMENTS.open(encoding="utf-8"):
        row = json.loads(line)
        if row.get("segment_id") == SEGMENT_ID:
            lines = SOURCE.read_text(encoding="utf-8").splitlines()
            start, end = int(row["line_start"]), int(row["line_end"])
            text = "\n".join(lines[start - 1 : end])
            if not text:
                raise ValueError("Could not reconstruct target source segment")
            return text
    raise ValueError(f"Segment not found in {SEGMENTS}")


def span(text: str, phrase: str, context: str | None = None) -> tuple[int, int]:
    if context is not None:
        context_start = text.find(context)
        if context_start < 0:
            raise ValueError(f"Missing source context: {context}")
        start = context_start + context.index(phrase)
        if text[start : start + len(phrase)] != phrase:
            raise ValueError(f"Source span mismatch for {phrase}")
        return start, start + len(phrase)
    start = text.find(phrase)
    if start < 0 or text.find(phrase, start + 1) >= 0:
        raise ValueError(f"Phrase missing or non-unique in source segment: {phrase}")
    return start, start + len(phrase)


def candidate(cid: str, name: str, kind: str, detail: str, line: int) -> dict[str, str]:
    return {
        "candidate_id": cid,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": kind,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
    }


def mention(mid: str, cid: str, surface: str, start: int, end: int, note: str = "") -> dict[str, str]:
    return {
        "mention_id": mid,
        "segment_id": SEGMENT_ID,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    }


def prepare() -> tuple[dict[Path, bytes], dict[Path, bytes], int, int]:
    cand_raw, cand_fields, cand_rows = load_csv(CANDIDATES)
    mention_raw, mention_fields, mention_rows = load_csv(MENTIONS)
    candidate_ids, mention_ids = next_ids(cand_rows, mention_rows)
    if NEW_STATEMENT_ID in {json.loads(line)["statement_id"] for line in STATEMENTS.open(encoding="utf-8")}:
        raise ValueError(f"Statement ID already exists: {NEW_STATEMENT_ID}")

    c_fund, c_shortage, c_limited, c_explanations, c_figures, c_torture = candidate_ids
    new_candidates = [
        candidate(c_fund, "Fundraising problem in Claudio Aquaviva's correspondence", "term",
                  "Haskell summarizes correspondence about raising more money, including selling jewels and soliciting gifts; no individual letters or completed transactions are identified.", 30),
        candidate(c_shortage, "Jesuit shortage of funds described as desperate", "term",
                  "Source-bound financial condition used by Haskell to explain the Jesuits' limited patronage contribution; no amount or precise duration is given.", 28),
        candidate(c_limited, "Limited Jesuit contribution to patronage in early church decoration", "term",
                  "Haskell's qualified assessment of the Jesuits' contribution; 'exceedingly limited' and 'however startling' remain source-attributed.", 28),
        candidate(c_explanations, "Unspecified torture explanations attached to the S. Stefano Rotondo frescoes", "",
                  "A source-defined group of explanatory texts attached to individual frescoes; exact wording, individual inscriptions, and total count are not supplied.", 22),
        candidate(c_figures, "Unnamed martyr and soldier depicted in the S. Vitale fresco cycle", "",
                  "Two depicted figures named only by role in Haskell's visual description; do not identify them as historical individuals.", 27),
        candidate(c_torture, "Torture as a predominant subject of the S. Vitale fresco cycle", "term",
                  "A source-bound iconographic subject; Haskell says the fresco subjects were almost exclusively concerned with torture.", 26),
    ]

    text = segment_text()
    known = next(r for r in mention_rows if r["mention_id"] == "m-chp3-secii-l19-31-0001")
    if int(known["start_char"]) != text.index("Gregory XIII"):
        raise ValueError("Reconstructed text offsets do not match the existing segment anchor")
    torture_context = "the subjects were almost exclusively concerned with torture"
    phrases = [
        ("the problem of how to raise more money", None),
        ("their desperate shortage of funds", None),
        ("contribution to patronage made by the Jesuits", None),
        ("the explanation of the torture", None),
        ("a martyr", None),
        ("a soldier", None),
        ("torture", torture_context),
    ]
    spans = [span(text, phrase, context) for phrase, context in phrases]
    new_mentions = [
        mention(mention_ids[0], c_fund, phrases[0][0], *spans[0], "Fundraising topic summarized from Aquaviva's correspondence; no individual letter identified."),
        mention(mention_ids[1], c_shortage, phrases[1][0], *spans[1], "Source's stated cause of the limited patronage contribution."),
        mention(mention_ids[2], c_limited, phrases[2][0], *spans[2], "Effect that the next sentence says was largely due to the shortage of funds."),
        mention(mention_ids[3], c_explanations, phrases[3][0], *spans[3], "The explanatory text is not transcribed; number and individual wording remain unspecified."),
        mention(mention_ids[4], c_figures, phrases[4][0], *spans[4], "Depicted role only; no historical identity supplied."),
        mention(mention_ids[5], c_figures, phrases[5][0], *spans[5], "Depicted role only; no historical identity supplied."),
        mention(mention_ids[6], c_torture, phrases[6][0], *spans[6], "Iconographic topic in the S. Vitale cycle, not a separate event."),
    ]

    statement_raw = STATEMENTS.read_bytes()
    statements = statement_raw.decode("utf-8").splitlines(keepends=True)
    targets = {
        "st-chp3-secii-l19-31-aquaviva-correspondence-raising-funds",
        "st-chp3-secii-l19-31-shortage-funds-explains-limited-patronage",
        "st-chp3-secii-l19-31-stefano-cycle-detail-and-explanations",
        "st-chp3-secii-l19-31-vitale-images-martyr-and-soldier",
        "st-chp3-secii-l19-31-vitale-subjects-mostly-torture",
    }
    all_targets = targets | NOTE2_LINK_IDS
    found: set[str] = set()
    for i, line in enumerate(statements):
        item = json.loads(line)
        sid = item.get("statement_id")
        if sid not in all_targets:
            continue
        found.add(sid)
        if sid in NOTE2_LINK_IDS:
            q = item.get("qualifiers") or {}
            linked = q.get("linked_body_statement_ids")
            old_id = "st-chp3-secii-l19-31-stefano-cycle-detail-and-explanations"
            if not isinstance(linked, list) or old_id not in linked:
                raise ValueError(f"Expected old body link in footnote statement {sid}")
            q["linked_body_statement_ids"] = [NEW_STATEMENT_ID if value == old_id else value for value in linked]
            item["qualifiers"] = q
            statements[i] = json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
            continue
        if item.get("segment_id") != SEGMENT_ID:
            raise ValueError(f"Unexpected segment for {sid}")
        q = item.setdefault("qualifiers", {})
        if sid.endswith("aquaviva-correspondence-raising-funds"):
            if item.get("object_candidate_id"):
                raise ValueError(f"Expected open object for {sid}")
            item["object_candidate_id"] = c_fund
            q["claim"] = "Haskell says Aquaviva's correspondence often concerns the problem of raising more money, including selling jewels and soliciting gifts."
            q["relation_candidate_note"] = "The phrase 'problem of how to raise more money' defines a source-bounded fundraising topic. Link that concept without inventing individual letters or claiming that the suggested sales and gifts occurred."
            q.pop("open_endpoint_reason", None)
        elif sid.endswith("shortage-funds-explains-limited-patronage"):
            if item.get("object_candidate_id"):
                raise ValueError(f"Expected open object for {sid}")
            item["subject_candidate_id"] = c_shortage
            item["object_candidate_id"] = c_limited
            q["claim"] = "Haskell says the Jesuits' desperate shortage of funds largely explains their exceedingly limited contribution to patronage."
            q["relation_candidate_note"] = "The prior clause names the effect as the Jesuits' limited contribution to patronage; 'This' in the following sentence says it was largely due to their desperate shortage of funds. Separate source-defined cause and effect concepts, preserving Haskell's qualification."
            q.pop("open_endpoint_reason", None)
        elif sid.endswith("stefano-cycle-detail-and-explanations"):
            q["claim"] = "Haskell says the S. Stefano Rotondo martyrdom frescoes were deliberately painted in great detail."
            q["relation_candidate"] = False
            q["relation_candidate_note"] = "This clause describes the visual treatment of one fresco cycle; it is an attributed work characteristic, not a relation between two entities. The attached explanatory texts are recorded separately."
            q.pop("open_endpoint_reason", None)
            item["original_quote"] = "They were deliberately painted in great detail"
        elif sid.endswith("vitale-images-martyr-and-soldier"):
            if item.get("object_candidate_id"):
                raise ValueError(f"Expected open object for {sid}")
            item["object_candidate_id"] = c_figures
            q["relation_candidate_note"] = "The fresco cycle is described as depicting a source-defined group consisting of an unnamed martyr and soldier. Map the depicted figures as a group with type unresolved; do not identify them as historical persons."
            q.pop("open_endpoint_reason", None)
        elif sid.endswith("vitale-subjects-mostly-torture"):
            if item.get("object_candidate_id"):
                raise ValueError(f"Expected open object for {sid}")
            item["object_candidate_id"] = c_torture
            q["relation_candidate_note"] = "The source explicitly names torture as the predominant subject concept. Map it to a source-bound term and retain 'almost exclusively' as Haskell's qualifier."
            q.pop("open_endpoint_reason", None)
        statements[i] = json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
    if found != all_targets:
        raise ValueError(f"Missing target statements: {sorted(all_targets - found)}")

    # The detailed-painting assertion stays under its existing ID; the attached-text relation is recorded atomically.
    new_statement = {
        "statement_id": NEW_STATEMENT_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-5019",
        "object_candidate_id": c_explanations,
        "predicate": "fresco_cycle_has_attached_torture_explanations",
        "qualifiers": {
            "source_line_start": 22,
            "source_line_end": 22,
            "claim": "Haskell says an explanation of torture was attached to each fresco in the S. Stefano Rotondo cycle.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "print_page": 67,
            "pdf_physical_page": 5,
            "qualification": "The explanatory text is not transcribed; no total count or individual wording is supplied.",
            "footnote_marker": 2,
            "footnote_page": 67,
            "footnote_linkage": "The source's note 2 is linked to the Jesuit Archives necrology statement st-chp3-secii-p67-note2-necrology and its quoted claim st-chp3-secii-p67-note2-necrology-claim.",
            "related_statement_ids": ["st-chp3-secii-l19-31-stefano-cycle-detail-and-explanations"],
            "relation_candidate": True,
            "relation_candidate_note": "The exact phrase 'the explanation of the torture was attached to each fresco' supports an attachment relation to a source-defined group of explanatory texts. Type and individual text identities remain open.",
        },
        "original_quote": "the explanation of the torture was attached to each fresco",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
    }
    statements.append(json.dumps(new_statement, ensure_ascii=False, separators=(",", ":")) + "\n")

    candidate_after = append_csv(cand_raw, cand_fields, new_candidates)
    mention_after = append_csv(mention_raw, mention_fields, new_mentions)
    statement_after = "".join(statements).encode("utf-8")
    paths = {
        CANDIDATES: candidate_after,
        MENTIONS: mention_after,
        STATEMENTS: statement_after,
    }
    backups = {p: p.with_name(f"{p.name}.{SUFFIX}") for p in paths}
    return paths, backups, len(cand_rows), len(mention_rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    paths, backups, candidate_count, mention_count = prepare()

    print(f"candidate_rows={candidate_count}->{candidate_count + 6}")
    print(f"mention_rows={mention_count}->{mention_count + 7}")
    print(f"statement_rows={sum(1 for _ in STATEMENTS.open(encoding='utf-8'))}->{sum(1 for _ in paths[STATEMENTS].decode('utf-8').splitlines())}")
    print(f"open_endpoints={open_count(STATEMENTS.read_bytes())}->{open_count(paths[STATEMENTS])}")
    for path, after in paths.items():
        print(f"{path.relative_to(ROOT)} {sha(path.read_bytes())}->{sha(after)}")
    print("planned candidates: cand-12308..cand-12313; mentions: m-chp3-secii-l19-31-0037..0043")
    print(f"planned statement: {NEW_STATEMENT_ID}")
    print("footnote links: replace the split body statement in both note-2 records")
    if args.preview:
        return 0

    existing_backups = [p for p in backups.values() if p.exists()]
    if existing_backups:
        raise FileExistsError(f"Refusing to overwrite recovery copies: {existing_backups}")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    temps: dict[Path, Path] = {}
    try:
        for path, data in paths.items():
            temp = path.with_name(f"{path.name}.tmp-{SUFFIX}")
            if temp.exists():
                raise FileExistsError(f"Refusing to overwrite temporary file: {temp}")
            temp.write_bytes(data)
            temps[path] = temp
        for path, temp in temps.items():
            temp.replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        raise
    for path, backup in backups.items():
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.relative_to(ROOT)}:{sha(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
