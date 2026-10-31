"""Preconditioned current-version repairs from the independent p.117 review."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
ALIGNMENTS = TABLES / "alignment.csv"
BACKUP_TAG = ".bak-s2-chp4-p117-current-review-followup-final-20261031"

NEW_CANDIDATE_ID = "cand-12465"
NEW_MENTIONS = {
    "m-chp4-sec-ii-p117-0036": {
        "candidate_id": "cand-11665",
        "surface_form": "the King and Queen and of two Infantas",
        "note": "Source-bounded sitter group; personal identities remain unresolved.",
    },
    "m-chp4-sec-ii-p117-0037": {
        "candidate_id": "cand-11666",
        "surface_form": "many of the older Roman buildings and paintings",
        "note": "Source-bounded mixed group; no individual building or painting is identified.",
    },
}

STATEMENT_UPDATES = {
    "st-chp4-sec-ii-p117-alexander-avoids-offending-french": {
        "qualifiers.claim": (
            "Haskell says Alexander VII was anxious to avoid offending the French.",
            "Haskell says Alexander VII was most anxious to avoid offending the French whenever possible.",
        ),
    },
    "st-chp4-sec-ii-p117-papal-policy-shift": {
        "qualifiers.claim": (
            "Haskell says a change of Pope in Rome led to a change in policy.",
            "Haskell says that, as so often happened, a change of Pope in Rome led to a change in policy.",
        ),
    },
    "st-chp4-sec-ii-p117-patronage-difficulty": {
        "qualifiers.claim": (
            "Haskell generalizes that disgrace made it difficult to procure work from fashionable modern artists.",
            "Haskell says that, as always, disgrace led to difficulties in procuring work from the most fashionable modern artists.",
        ),
    },
    "st-chp4-sec-ii-p117-spanish-backing": {
        "object_candidate_id": ("cand-4591", NEW_CANDIDATE_ID),
        "qualifiers.claim": (
            "Haskell says Massimi backed the Spaniards in their quarrels with France, apparently to counter his reputation.",
            "Haskell reports that, as if to belie his damaging reputation, Massimi wholeheartedly backed the Spaniards in their quarrels with France.",
        ),
        "qualifiers.mentioned_candidate_ids": (
            ["cand-1564", "cand-4591", "cand-4632"],
            ["cand-1564", NEW_CANDIDATE_ID, "cand-4632"],
        ),
        "qualifiers.relation_candidate_note": (
            "Records Massimi backing Spain as a political side; France is retained as context and a separate statement records the named quarrel.",
            "Records Haskell’s claim that Massimi wholeheartedly backed an unidentified collective of Spaniards; do not equate this group with the Spain polity cand-4591.",
        ),
    },
    "st-chp4-sec-ii-p117-spanish-french-quarrels": {
        "subject_candidate_id": ("cand-4591", NEW_CANDIDATE_ID),
        "qualifiers.mentioned_candidate_ids": (
            ["cand-4591", "cand-4632"],
            [NEW_CANDIDATE_ID, "cand-4632"],
        ),
        "qualifiers.relation_candidate_note": (
            "Political sides are named; cause and external details are not supplied.",
            "Haskell attributes the quarrel with France to an unidentified collective of Spaniards; keep distinct from Spain polity cand-4591.",
        ),
    },
    "st-chp4-sec-ii-p117-french-protested-violently": {
        "qualifiers.mentioned_candidate_ids": (
            ["cand-5968", "cand-4591", "cand-4632", "cand-5977"],
            ["cand-5968", "cand-4591", "cand-4632", "cand-5977", "cand-3462"],
        ),
    },
}

CANDIDATE_ROW = {
    "candidate_id": NEW_CANDIDATE_ID,
    "index_entry_id": "",
    "canonical_name": "Unidentified Spaniards acting in the p.117 France quarrels",
    "index_page_range": "",
    "suggested_type": "",
    "status": "open",
    "index_source_file": "",
    "sub_entry": "",
    "detail": "Source-bounded collective actor: Haskell says Massimi wholeheartedly backed the Spaniards in their quarrels with France. The passage does not identify a government, organization, or individual participants. Keep distinct from cand-4591 Spain polity; type remains unresolved.",
    "exclude_reason": "",
    "candidate_origin": "body-mention",
    "candidate_source_ref": "chp-4:04_CHP-4_sec_ii:l207-216#L208",
}


def get_path(record: dict, dotted: str) -> tuple[dict, str]:
    parts = dotted.split(".")
    parent = record
    for part in parts[:-1]:
        parent = parent[part]
    return parent, parts[-1]


def load_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]], str, bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    fields = reader.fieldnames
    if not fields:
        raise SystemExit(f"missing CSV header: {path}")
    rows = list(reader)
    return raw, fields, rows, eol, has_bom


def encode_csv_row(fields: list[str], row: dict[str, str], eol: str) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator=eol)
    writer.writerow(row)
    return buffer.getvalue().encode("utf-8")


def append_csv_rows(raw: bytes, fields: list[str], rows: list[dict[str, str]], eol: str, has_bom: bool) -> bytes:
    prefix = b"\xef\xbb\xbf" if has_bom else b""
    body = raw[len(prefix):] if has_bom else raw
    eol_bytes = eol.encode("ascii")
    if body and not body.endswith((b"\n", b"\r")):
        body += eol_bytes
    for row in rows:
        body += encode_csv_row(fields, row, eol)
    return prefix + body


def patch_and_append_csv_row(
    raw: bytes,
    fields: list[str],
    target_id: str,
    id_field: str,
    updates: dict[str, tuple[str, str]],
    additions: list[dict[str, str]],
    eol: str,
    has_bom: bool,
) -> bytes:
    text = raw.decode("utf-8-sig")
    physical_lines = text.splitlines(keepends=True)
    reader = csv.reader(io.StringIO(text, newline=""))
    out: list[str] = []
    cursor = 0
    header = next(reader)
    out.extend(physical_lines[: reader.line_num])
    cursor = reader.line_num
    found = 0
    for values in reader:
        end_line = reader.line_num
        original_record = "".join(physical_lines[cursor:end_line])
        cursor = end_line
        row = dict(zip(fields, values))
        if row.get(id_field) == target_id:
            found += 1
            for key, (expected, replacement) in updates.items():
                if row.get(key) != expected:
                    raise SystemExit(f"CSV row precondition failed: {target_id} {key}")
                row[key] = replacement
            out.append(encode_csv_row(fields, row, eol).decode("utf-8"))
        else:
            out.append(original_record)
    if found != 1:
        raise SystemExit(f"expected one CSV row for {target_id}, found {found}")
    out.extend(physical_lines[cursor:])
    serialized = "".join(out).encode("utf-8")
    if has_bom:
        serialized = b"\xef\xbb\xbf" + serialized
    return append_csv_rows(serialized, fields, additions, eol, has_bom)


def render_jsonl_updates() -> tuple[bytes, list[str]]:
    raw = STATEMENTS.read_bytes()
    found: set[str] = set()
    changed: list[str] = []
    output: list[bytes] = []
    for line in raw.splitlines(keepends=True):
        ending = b"\r\n" if line.endswith(b"\r\n") else b"\n" if line.endswith(b"\n") else b""
        payload = line[: -len(ending)] if ending else line
        record = json.loads(payload.decode("utf-8"))
        statement_id = record.get("statement_id")
        updates = STATEMENT_UPDATES.get(statement_id)
        if not updates:
            output.append(line)
            continue
        if statement_id in found:
            raise SystemExit(f"duplicate statement_id: {statement_id}")
        found.add(statement_id)
        for dotted, (expected, replacement) in updates.items():
            parent, key = get_path(record, dotted)
            if parent[key] != expected:
                raise SystemExit(f"statement precondition failed: {statement_id} {dotted}")
            parent[key] = replacement
        output.append(json.dumps(record, ensure_ascii=False).encode("utf-8") + ending)
        changed.append(statement_id)
    missing = sorted(set(STATEMENT_UPDATES) - found)
    if missing:
        raise SystemExit(f"missing statement IDs: {missing}")
    return b"".join(output), changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidate_rows, candidate_eol, candidate_bom = load_csv(CANDIDATES)
    alignment_raw, alignment_fields, alignment_rows, alignment_eol, alignment_bom = load_csv(ALIGNMENTS)
    mention_raw, mention_fields, mention_rows, mention_eol, mention_bom = load_csv(MENTIONS)

    if any(row["candidate_id"] == NEW_CANDIDATE_ID for row in candidate_rows):
        raise SystemExit(f"candidate already exists: {NEW_CANDIDATE_ID}")
    if any(row["candidate_id"] == NEW_CANDIDATE_ID for row in alignment_rows):
        raise SystemExit(f"alignment already exists for {NEW_CANDIDATE_ID}")

    next_alignment_number = max(
        int(match.group(1))
        for row in alignment_rows
        if (match := re.fullmatch(r"aln-(\d+)", row["alignment_id"]))
    ) + 1
    alignment_id = f"aln-{next_alignment_number:04d}"

    existing_mentions = {row["mention_id"]: row for row in mention_rows}
    old_actor = existing_mentions.get("m-chp4-sec-ii-p117-0011")
    if not old_actor or (
        old_actor["candidate_id"], old_actor["surface_form"], old_actor["start_char"], old_actor["end_char"], old_actor["note"]
    ) != ("cand-4591", "Spaniards", "386", "395", "Spanish political actor."):
        raise SystemExit("precondition failed for m-chp4-sec-ii-p117-0011")
    for mention_id in NEW_MENTIONS:
        if mention_id in existing_mentions:
            raise SystemExit(f"mention already exists: {mention_id}")

    source_lines = (ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md").read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[206:216])
    for mention_id, definition in NEW_MENTIONS.items():
        surface = definition["surface_form"]
        if segment_text.count(surface) != 1:
            raise SystemExit(f"source span is not unique for {mention_id}: {surface}")
        start = segment_text.index(surface)
        definition["start_char"] = str(start)
        definition["end_char"] = str(start + len(surface))

    old_actor["candidate_id"] = NEW_CANDIDATE_ID
    old_actor["note"] = "Source-bounded collective actor; distinct from Spain polity cand-4591."
    for mention_id, definition in NEW_MENTIONS.items():
        mention_rows.append(
            {
                "mention_id": mention_id,
                "segment_id": "chp-4:04_CHP-4_sec_ii:l207-216",
                "candidate_id": definition["candidate_id"],
                "surface_form": definition["surface_form"],
                "start_char": definition["start_char"],
                "end_char": definition["end_char"],
                "note": definition["note"],
            }
        )

    candidate_rows.append(CANDIDATE_ROW.copy())
    alignment_rows.append(
        {
            "alignment_id": alignment_id,
            "candidate_id": NEW_CANDIDATE_ID,
            "ku_id": "",
            "external_source": "",
            "external_id": "",
            "decision": "undecided",
            "accessed_date": "",
            "process_ref": "S3-full-book-2026-10-15",
            "legacy_ku_id": "",
            "resolution_note": (
                f"group=sg3-untyped-cand-12465; source_ref=chp-4:04_CHP-4_sec_ii:l207-216#"
                f"m-chp4-sec-ii-p117-0037; Haskell’s collective ‘Spaniards’ is not enough to identify a "
                "government or bounded organization; keep distinct from cand-4591 Spain polity and leave type unresolved."
            ),
        }
    )

    statements_after, changed_statements = render_jsonl_updates()
    mention_additions = [
        {
            "mention_id": mention_id,
            "segment_id": "chp-4:04_CHP-4_sec_ii:l207-216",
            "candidate_id": definition["candidate_id"],
            "surface_form": definition["surface_form"],
            "start_char": definition["start_char"],
            "end_char": definition["end_char"],
            "note": definition["note"],
        }
        for mention_id, definition in NEW_MENTIONS.items()
    ]
    mentions_after = patch_and_append_csv_row(
        mention_raw,
        mention_fields,
        "m-chp4-sec-ii-p117-0011",
        "mention_id",
        {
            "candidate_id": ("cand-4591", NEW_CANDIDATE_ID),
            "note": ("Spanish political actor.", "Source-bounded collective actor; distinct from Spain polity cand-4591."),
        },
        mention_additions,
        mention_eol,
        mention_bom,
    )
    candidate_after = append_csv_rows(candidate_raw, candidate_fields, [CANDIDATE_ROW], candidate_eol, candidate_bom)
    alignment_after = append_csv_rows(
        alignment_raw,
        alignment_fields,
        [
            {
                "alignment_id": alignment_id,
                "candidate_id": NEW_CANDIDATE_ID,
                "ku_id": "",
                "external_source": "",
                "external_id": "",
                "decision": "undecided",
                "accessed_date": "",
                "process_ref": "S3-full-book-2026-10-15",
                "legacy_ku_id": "",
                "resolution_note": (
                    f"group=sg3-untyped-cand-12465; source_ref=chp-4:04_CHP-4_sec_ii:l207-216#"
                    f"m-chp4-sec-ii-p117-0011; Haskell’s collective ‘Spaniards’ is not enough to identify a "
                    "government or bounded organization; keep distinct from cand-4591 Spain polity and leave type unresolved."
                ),
            }
        ],
        alignment_eol,
        alignment_bom,
    )
    new_files = {
        STATEMENTS: statements_after,
        MENTIONS: mentions_after,
        CANDIDATES: candidate_after,
        ALIGNMENTS: alignment_after,
    }
    print(f"statement_rows_changed={len(changed_statements)} ids={','.join(changed_statements)}")
    print(f"mention_rows_added={len(NEW_MENTIONS)} remapped=m-chp4-sec-ii-p117-0011")
    for mention_id, definition in NEW_MENTIONS.items():
        print(f"{mention_id} | {definition['candidate_id']} | {definition['start_char']}:{definition['end_char']} | {definition['surface_form']}")
    print(f"candidate_added={NEW_CANDIDATE_ID}; alignment_added={alignment_id}:undecided")
    if not args.apply:
        print("DRY RUN: no files written")
        return 0

    for path in new_files:
        backup = path.with_name(path.name + BACKUP_TAG)
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    for path, payload in new_files.items():
        backup = path.with_name(path.name + BACKUP_TAG)
        shutil.copy2(path, backup)
        temp = path.with_suffix(path.suffix + ".tmp")
        temp.write_bytes(payload)
        temp.replace(path)
        print(f"updated={path.relative_to(ROOT)} backup={backup.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
