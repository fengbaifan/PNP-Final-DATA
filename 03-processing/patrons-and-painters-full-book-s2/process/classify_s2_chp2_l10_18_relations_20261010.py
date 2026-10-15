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
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
SEGMENT = "chp-2:02_CHP-2_sec_ii:l10-18"
EXPECTED_HASHES = {
    STATEMENTS.name: "1887cd1731e90f73de73d9d1a938da0d97ccc7bb509bc902404f2d4cdef1ed0c",
    CANDIDATES.name: "3643981fd7dc5829bfb4778a118f279acfe40a279cbd10b507fc82edbea3ca85",
    MENTIONS.name: "d16b5649889babf5c7e14cce2c089a95a197b2e6ac9d92dea9442cc5acda465a",
}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp2-sec-ii-l10-18-20261010"),
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + ".bak-s2-chp2-sec-ii-l10-18-20261010"),
    MENTIONS: MENTIONS.with_name(MENTIONS.name + ".bak-s2-chp2-sec-ii-l10-18-20261010"),
}
TRUE_NOTES = {
    "st-chp2-sec-ii-l10-18-contarini-state-and-rome-description":
        "The source attributes a description of the Pope's state and Rome to Contarini; cand-1831 preserves the additional state referent, while the emporium language remains rhetorical.",
    "st-chp2-sec-ii-l10-18-contarini-visitors-and-tribute":
        "The claim concerns an unnamed group of people coming to Rome from every country. The source-defined open collective is the subject; the tribute wording remains figurative and attributed to Contarini.",
    "st-chp2-sec-ii-l10-18-european-power-and-rome-prestige":
        "Haskell explicitly links the growth of European nation-state power with Rome's increasing reliance on grandeur for prestige. Preserve this as an authorial historical interpretation, not a general causal law.",
    "st-chp2-sec-ii-l10-18-papal-financial-patronage":
        "The source explicitly scopes the Pope's financial patronage across Italy; no individual recipient or transaction is inferred.",
    "st-chp2-sec-ii-l10-18-urban-professed-wealth-policy":
        "This records Urban VIII's professed intention regarding the wealth of the Papal States; it does not assert sincerity or implementation.",
}
VISITOR_CANDIDATE = {
    "candidate_id": "cand-11583",
    "index_entry_id": "",
    "canonical_name": "Visitors from every country to Rome (Contarini's 1623 collective reference)",
    "index_page_range": "",
    "suggested_type": "",
    "status": "open",
    "index_source_file": "",
    "sub_entry": "",
    "detail": (
        "Contarini's quotation says people came to Rome from every country to see its splendours and "
        "figuratively pay tribute. No individual visitors, count, or narrower group membership is named."
    ),
    "exclude_reason": "",
    "candidate_origin": "body-mention",
    "candidate_source_ref": f"{SEGMENT}#L15",
}
VISITOR_MENTION_ID = "m-chp2-secii-l10-18-0036"
VISITOR_SURFACE = "people come from every country"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[list[dict], list[str], bytes]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or []), raw


def write_csv(path: Path, rows: list[dict], fields: list[str], raw: bytes) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return prefix + output.getvalue().encode("utf-8")


def read_jsonl(path: Path) -> tuple[list[dict], bytes]:
    raw = path.read_bytes()
    return [json.loads(line.decode("utf-8-sig")) for line in raw.splitlines() if line.strip()], raw


def write_jsonl(rows: list[dict], raw: bytes) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    lines = []
    for index, row in enumerate(rows):
        line = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and raw.startswith(b"\xef\xbb\xbf"):
            line = b"\xef\xbb\xbf" + line
        lines.append(line + newline)
    return b"".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply reviewed relation classifications and endpoint repairs")
    args = parser.parse_args()
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        actual = sha256(path.read_bytes())
        require(actual == EXPECTED_HASHES[path.name], f"{path.name} changed since review: {actual}")
    for path, backup in BACKUPS.items():
        require(not backup.exists(), f"recovery backup already exists: {backup.name}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    require(len(source_lines) >= 15, "source line 15 is missing")
    require(VISITOR_SURFACE in source_lines[14], "visitor group source phrase changed")
    source_text = "\n".join(source_lines[9:18])
    local_start = sum(len(source_lines[index - 1]) + 1 for index in range(10, 15))
    local_start += source_lines[14].index(VISITOR_SURFACE)
    local_end = local_start + len(VISITOR_SURFACE)
    require(source_text[local_start:local_end] == VISITOR_SURFACE, "visitor mention span does not match source")

    statements, statement_raw = read_jsonl(STATEMENTS)
    candidates, candidate_fields, candidate_raw = read_csv(CANDIDATES)
    mentions, mention_fields, mention_raw = read_csv(MENTIONS)
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    require(len(statement_by_id) == len(statements), "duplicate statement_id")
    require(len(candidate_by_id) == len(candidates), "duplicate candidate_id")
    require(len(mention_by_id) == len(mentions), "duplicate mention_id")
    expected_ids = set(TRUE_NOTES)
    pending_bilateral = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT
        and row.get("subject_candidate_id") and row.get("object_candidate_id")
        and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    require(pending_bilateral == expected_ids,
            f"pending bilateral statement set changed: {sorted(pending_bilateral ^ expected_ids)}")
    require(max(int(row["candidate_id"].split("-")[1]) for row in candidates) == 11582,
            "candidate table changed since candidate allocation")
    require(VISITOR_CANDIDATE["candidate_id"] not in candidate_by_id, "visitor candidate ID already exists")
    require(VISITOR_MENTION_ID not in mention_by_id, "visitor mention ID already exists")
    natural_keys = {
        (row["canonical_name"].casefold().strip(), row["suggested_type"].casefold().strip())
        for row in candidates
    }
    key = (VISITOR_CANDIDATE["canonical_name"].casefold().strip(), VISITOR_CANDIDATE["suggested_type"].casefold().strip())
    require(key not in natural_keys, "visitor candidate natural-key collision")
    require(candidate_fields == list(VISITOR_CANDIDATE), "candidate field order changed")
    new_mention = {
        "mention_id": VISITOR_MENTION_ID,
        "segment_id": SEGMENT,
        "candidate_id": VISITOR_CANDIDATE["candidate_id"],
        "surface_form": VISITOR_SURFACE,
        "start_char": str(local_start),
        "end_char": str(local_end),
        "note": "Unnamed collective in Contarini's quotation: people who come to Rome from every country; no individual members or count is supplied.",
    }
    require(mention_fields == list(new_mention), "mention field order changed")

    expected_endpoints = {
        "st-chp2-sec-ii-l10-18-contarini-state-and-rome-description": ("cand-0823", "cand-3126"),
        "st-chp2-sec-ii-l10-18-contarini-visitors-and-tribute": ("cand-0823", "cand-3126"),
        "st-chp2-sec-ii-l10-18-european-power-and-rome-prestige": ("cand-4220", "cand-3126"),
        "st-chp2-sec-ii-l10-18-papal-financial-patronage": ("cand-3104", "cand-3114"),
        "st-chp2-sec-ii-l10-18-urban-professed-wealth-policy": ("cand-3104", "cand-1831"),
    }
    for statement_id, note in TRUE_NOTES.items():
        row = statement_by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        start = qualifiers.get("source_line_start")
        end = qualifiers.get("source_line_end")
        require(row.get("segment_id") == SEGMENT, f"{statement_id} is outside the reviewed segment")
        require((row.get("subject_candidate_id"), row.get("object_candidate_id")) == expected_endpoints[statement_id],
                f"{statement_id} endpoints changed")
        require(qualifiers.get("relation_candidate") is None, f"{statement_id} is already classified")
        require(isinstance(start, int) and isinstance(end, int) and 10 <= start <= end <= 18,
                f"{statement_id} has an invalid source anchor")
        anchor = "\n".join(source_lines[start - 1:end])
        require(row.get("original_quote") in anchor, f"{statement_id} quote no longer matches source")
        qualifiers = dict(qualifiers)
        qualifiers["relation_candidate"] = True
        qualifiers["relation_candidate_note"] = note
        row["qualifiers"] = qualifiers

    state_quote = statement_by_id["st-chp2-sec-ii-l10-18-contarini-state-and-rome-description"]
    state_q = dict(state_quote["qualifiers"])
    state_q["other_candidate_ids"] = ["cand-1831"]
    state_q["mentioned_candidate_ids"] = ["cand-0823", "cand-1831", "cand-3126"]
    state_quote["qualifiers"] = state_q

    visitors = statement_by_id["st-chp2-sec-ii-l10-18-contarini-visitors-and-tribute"]
    visitors["subject_candidate_id"] = VISITOR_CANDIDATE["candidate_id"]
    visitors["predicate"] = "collective_visitation_reported"
    visitors_q = dict(visitors["qualifiers"])
    visitors_q["mentioned_candidate_ids"] = ["cand-0823", VISITOR_CANDIDATE["candidate_id"], "cand-3126"]
    visitors["qualifiers"] = visitors_q

    projected_candidates = candidates + [VISITOR_CANDIDATE]
    projected_mentions = mentions + [new_mention]
    projected_ids = {row["candidate_id"] for row in projected_candidates}
    for row in statements:
        if row.get("segment_id") == SEGMENT:
            for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
                require(not endpoint or endpoint in projected_ids, f"missing candidate endpoint: {row['statement_id']}")
    for mention in projected_mentions:
        if mention.get("segment_id") == SEGMENT:
            start, end = int(mention["start_char"]), int(mention["end_char"])
            require(0 <= start < end <= len(source_text), f"invalid mention span: {mention['mention_id']}")
            require(source_text[start:end] == mention["surface_form"], f"mention/source mismatch: {mention['mention_id']}")

    before = {
        "relation_true_bilateral": sum(1 for row in statements if row.get("subject_candidate_id") and row.get("object_candidate_id") and (row.get("qualifiers") or {}).get("relation_candidate") is True) - 5,
        "relation_false_bilateral": sum(1 for row in statements if row.get("subject_candidate_id") and row.get("object_candidate_id") and (row.get("qualifiers") or {}).get("relation_candidate") is False),
        "unclassified_bilateral": sum(1 for row in statements if row.get("subject_candidate_id") and row.get("object_candidate_id") and (row.get("qualifiers") or {}).get("relation_candidate") is None) + 5,
    }
    after = {
        "relation_true_bilateral": sum(1 for row in statements if row.get("subject_candidate_id") and row.get("object_candidate_id") and (row.get("qualifiers") or {}).get("relation_candidate") is True),
        "relation_false_bilateral": sum(1 for row in statements if row.get("subject_candidate_id") and row.get("object_candidate_id") and (row.get("qualifiers") or {}).get("relation_candidate") is False),
        "unclassified_bilateral": sum(1 for row in statements if row.get("subject_candidate_id") and row.get("object_candidate_id") and (row.get("qualifiers") or {}).get("relation_candidate") is None),
    }
    require(before == {"relation_true_bilateral": 3983, "relation_false_bilateral": 451, "unclassified_bilateral": 4063},
            f"unexpected before counts: {before}")
    require(after == {"relation_true_bilateral": 3988, "relation_false_bilateral": 451, "unclassified_bilateral": 4058},
            f"unexpected projected counts: {after}")

    payload = {
        STATEMENTS: write_jsonl(statements, statement_raw),
        CANDIDATES: write_csv(CANDIDATES, projected_candidates, candidate_fields, candidate_raw),
        MENTIONS: write_csv(MENTIONS, projected_mentions, mention_fields, mention_raw),
    }
    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "classified_true": list(TRUE_NOTES),
        "classified_false": [],
        "new_candidate": VISITOR_CANDIDATE,
        "new_mention": new_mention,
        "repaired_endpoints": {
            "Contarini_state_object_candidates": ["cand-1831", "cand-3126"],
            "visitors_subject": ["cand-0823", "cand-11583"],
        },
        "before": before,
        "after": after,
        "payload_sha256": {path.name: sha256(data) for path, data in payload.items()},
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write.")
        return

    originals = {path: path.read_bytes() for path in payload}
    written: list[Path] = []
    try:
        for path, backup in BACKUPS.items():
            shutil.copy2(path, backup)
        for path, data in payload.items():
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                handle.write(data)
                temp_path = Path(handle.name)
            os.replace(temp_path, path)
            written.append(path)
        actual_statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        actual_candidates, _, _ = read_csv(CANDIDATES)
        actual_mentions, _, _ = read_csv(MENTIONS)
        actual_by_id = {row["statement_id"]: row for row in actual_statements}
        require(len(actual_statements) == len(statements), "statement count changed")
        require(len(actual_candidates) == len(candidates) + 1, "candidate count did not increase by one")
        require(len(actual_mentions) == len(mentions) + 1, "mention count did not increase by one")
        require(all((actual_by_id[key].get("qualifiers") or {}).get("relation_candidate") is True for key in TRUE_NOTES),
                "one or more classifications were not persisted")
        require(actual_by_id["st-chp2-sec-ii-l10-18-contarini-visitors-and-tribute"]["subject_candidate_id"] == "cand-11583",
                "visitor endpoint repair was not persisted")
    except Exception:
        for path in written:
            path.write_bytes(originals[path])
        raise
    print(json.dumps({
        "result": "applied",
        "candidate_count": len(actual_candidates),
        "mention_count": len(actual_mentions),
        "statement_count": len(actual_statements),
        "sha256": {path.name: sha256(path.read_bytes()) for path in payload},
        "backups": [backup.name for backup in BACKUPS.values()],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
