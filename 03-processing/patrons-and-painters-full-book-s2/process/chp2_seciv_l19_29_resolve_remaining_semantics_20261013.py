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
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l19-29"
SEGMENT_SHA = "06b98701267f8db00f7dc1b9fa35e8ffcdc5d0951ba8c9c0a9e56347885e5fbd"
SOURCE_SHA = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
BACKUP_SUFFIX = ".bak-s2-chp2-seciv-l19-29-semantics-20261013"
EXPECTED = {
    "book-statements.jsonl": "4c761cc6402e88c10445014e8951da1ed4c825a7364fda072c18adfae6bac83e",
    "entity-candidates.csv": "dcce40f3b1d7b1cd4c7c10e8962f79f7c588be418c9737af4fd2f69e8114fb74",
    "mentions.csv": "e8769d49402b02dac6800f06c3f16970ab58a8c66eb1f37ba1dfd2bf3a9ee856",
    "s2-coverage.csv": "426c2cda4ed677ad7ad95a973858400abbf0b1c6d6d5b655ae31bbb54ffff9ad",
}
UNSET_IDS = {
    "st-chp2-seciv-l19-29-committee-lists-amended",
    "st-chp2-seciv-l19-29-germanicus-style-assessment",
    "st-chp2-seciv-l19-29-reassignment-accepted",
    "st-chp2-seciv-l19-29-samson-disappeared",
    "st-chp2-seciv-l19-29-triumph-evaluation",
}
NEW_DISCUSSION_ID = "st-chp2-seciv-l19-29-committee-discussion-frequency"
PRIOR_COMMITTEE_ID = "st-chp2-seciv-l6-17-committee-correspondence-and-list-preparation"
CITATION_ID = "st-chp2-seciv-l190-245-citation-05"
LIST_QUOTE = "up and amended"
DISCUSSION_QUOTE = "discussions were frequent."


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def serialize(name: str, rows: list[dict]) -> bytes:
    if name.endswith(".jsonl"):
        return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")


def append_unique(values: list[str], additions: list[str]) -> list[str]:
    return list(dict.fromkeys([*values, *additions]))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resolve remaining S2 claims and separate committee list activity from discussion frequency in CHP-2 section IV, L19-29."
    )
    parser.add_argument("--apply", action="store_true", help="write after protected checks; default is preview")
    args = parser.parse_args()
    paths = {name: TABLES / name for name in EXPECTED}
    for name, expected in EXPECTED.items():
        actual = digest(paths[name])
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected section source asset changed")
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected print-p.45 source segment fingerprint changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates = read_csv(paths["entity-candidates.csv"])
    mentions = read_csv(paths["mentions.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != UNSET_IDS:
        raise SystemExit(f"unexpected unset statement set: {sorted(unset)}")
    if NEW_DISCUSSION_ID in statement_by_id:
        raise SystemExit("planned committee discussion statement ID already exists")
    required_ids = {
        *UNSET_IDS,
        PRIOR_COMMITTEE_ID,
        CITATION_ID,
        "st-chp2-seciv-l19-29-francesco-main-picture-cortona-proposal",
        "st-chp2-seciv-l19-29-francesco-small-picture-poussin-proposal",
    }
    if required_ids - statement_by_id.keys():
        raise SystemExit(f"required statements missing: {sorted(required_ids - statement_by_id.keys())}")
    candidate_ids = {row["candidate_id"] for row in candidates}
    needed_candidates = {"cand-4306", "cand-2003", "cand-3035", "cand-2024", "cand-4612"}
    if not needed_candidates.issubset(candidate_ids):
        raise SystemExit(f"required candidates missing: {sorted(needed_candidates - candidate_ids)}")
    source_text = SOURCE.read_text(encoding="utf-8-sig")
    if any(quote not in source_text for quote in (LIST_QUOTE, DISCUSSION_QUOTE)):
        raise SystemExit("protected committee quotes no longer match the source")
    if len([row for row in coverage if row.get("segment_id") == SEGMENT_ID]) != 1:
        raise SystemExit("expected one print-p.45 L19-29 coverage row")
    citation = statement_by_id[CITATION_ID]
    if citation.get("segment_id") != "chp-2:02_CHP-2_sec_iv:l190-245":
        raise SystemExit("expected note-1 citation statement in the section IV notes segment")

    committee = statement_by_id["st-chp2-seciv-l19-29-committee-lists-amended"]
    committee["original_quote"] = LIST_QUOTE
    committee_q = committee.setdefault("qualifiers", {})
    committee_q["claim"] = "Haskell says the St Peter's committee's lists were amended."
    committee_q["qualification"] = (
        "The list contents and individual entries are unspecified; this continues the preceding segment's statement that lists were being drawn."
    )
    committee_q["relation_candidate"] = True
    committee_q["relation_candidate_note"] = (
        "The text explicitly reports amendment of the committee's lists; the specific lists and entries remain unidentified."
    )
    committee_q["open_endpoint_reason"] = "No specific list, list contents, or individual entries are identified."
    committee_q["mentioned_candidate_ids"] = ["cand-4306"]
    committee_q["related_statement_ids"] = append_unique(
        committee_q.get("related_statement_ids", []), [PRIOR_COMMITTEE_ID, CITATION_ID, NEW_DISCUSSION_ID]
    )
    committee_q["continuation_of_statement_id"] = PRIOR_COMMITTEE_ID

    discussion = {
        "statement_id": NEW_DISCUSSION_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-4306",
        "object_candidate_id": None,
        "predicate": "committee_discussion_frequency_reported",
        "qualifiers": {
            "source_line_start": 20,
            "source_line_end": 20,
            "claim": "Haskell says discussions in the committee's selection process were frequent.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "print_page": 45,
            "pdf_physical_page": 30,
            "footnote_marker": 1,
            "footnote_segment": "chp-2:02_CHP-2_sec_iv:l190-245",
            "footnote_refs": [
                {"marker": 1, "segment_id": "chp-2:02_CHP-2_sec_iv:l190-245", "source_line": 195}
            ],
            "qualification": "The source gives no count, participants, or discussion topics.",
            "relation_candidate": False,
            "relation_candidate_note": (
                "This records Haskell's qualitative frequency description of the committee process; no bounded discussion event, "
                "participant group, or topic is identified as a separate relation endpoint."
            ),
            "mentioned_candidate_ids": ["cand-4306"],
            "related_statement_ids": ["st-chp2-seciv-l19-29-committee-lists-amended", CITATION_ID],
        },
        "original_quote": DISCUSSION_QUOTE,
        "origin": "book",
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }
    statements.append(discussion)

    committee_q["related_statement_ids"] = append_unique(committee_q["related_statement_ids"], [NEW_DISCUSSION_ID])
    citation_q = citation.setdefault("qualifiers", {})
    linked_ids = citation_q.get("linked_body_statement_ids", [])
    citation_q["linked_body_statement_ids"] = append_unique(
        linked_ids, [PRIOR_COMMITTEE_ID, committee["statement_id"], NEW_DISCUSSION_ID]
    )
    citation_q["related_statement_ids"] = append_unique(
        citation_q.get("related_statement_ids", []), [PRIOR_COMMITTEE_ID, committee["statement_id"], NEW_DISCUSSION_ID]
    )

    style = statement_by_id["st-chp2-seciv-l19-29-germanicus-style-assessment"]
    style_q = style.setdefault("qualifiers", {})
    style_q["relation_candidate"] = False
    style_q["relation_candidate_note"] = (
        "This is Haskell's visual interpretation of Poussin's composition and later style, not an entity relation."
    )
    style_q["mentioned_candidate_ids"] = ["cand-2003"]

    acceptance = statement_by_id["st-chp2-seciv-l19-29-reassignment-accepted"]
    acceptance_q = acceptance.setdefault("qualifiers", {})
    acceptance_q["claim"] = "Haskell says the proposed reassignment of the main and smaller pictures was accepted."
    acceptance_q["qualification"] = (
        "Acceptance is reported, but the approving authority is not named; do not infer that the committee approved it solely from context. "
        "Acceptance does not establish completion or installation."
    )
    acceptance_q["relation_candidate"] = True
    acceptance_q["relation_candidate_note"] = (
        "The source explicitly reports acceptance of the two linked picture-reassignment proposals, while leaving the accepting authority unnamed."
    )
    acceptance_q["open_endpoint_reason"] = "The approving authority is not identified in the source."
    acceptance_q["mentioned_candidate_ids"] = ["cand-3035"]

    samson = statement_by_id["st-chp2-seciv-l19-29-samson-disappeared"]
    samson_q = samson.setdefault("qualifiers", {})
    samson_q["relation_candidate"] = False
    samson_q["relation_candidate_note"] = (
        "This is a book-reported status of the Samson picture, not a relation to an identified person or place and not a current location check."
    )
    samson_q["mentioned_candidate_ids"] = ["cand-2024"]

    triumph = statement_by_id["st-chp2-seciv-l19-29-triumph-evaluation"]
    triumph_q = triumph.setdefault("qualifiers", {})
    triumph_q["relation_candidate"] = False
    triumph_q["relation_candidate_note"] = (
        "This is Haskell's metaphorical summary of the young artists' success, not a bounded event or entity relation."
    )
    triumph_q["mentioned_candidate_ids"] = ["cand-4612"]

    if any(
        row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
        for row in statements
    ):
        raise SystemExit("section IV L19-29 still has unset relation_candidate values")
    coverage_row = next(row for row in coverage if row.get("segment_id") == SEGMENT_ID)
    coverage_note = (
        " 本轮完成5条旧unset：名单修订作为关系候选并与L17委员会来信/制表片段衔接；委员会讨论频率单列为非关系描述并链接注1。"
        "提案获接受保留为审批主体未明的关系候选；Germanicus构图评价、Samson失去状态及青年艺术家“胜利完成”均保留为非关系陈述。"
        "印刷p.45（PDF物理第30页）已核对；来源资产未改。"
    )
    if coverage_note.strip() not in coverage_row["note"]:
        coverage_row["note"] = coverage_row["note"].rstrip() + coverage_note

    updated = {"book-statements.jsonl": statements, "s2-coverage.csv": coverage}
    payloads = {name: serialize(name, data) for name, data in updated.items()}
    result = {
        "mode": "apply" if args.apply else "preview",
        "segment": SEGMENT_ID,
        "closed_unset_ids": sorted(UNSET_IDS),
        "classifications": {
            "false": [
                "st-chp2-seciv-l19-29-germanicus-style-assessment",
                NEW_DISCUSSION_ID,
                "st-chp2-seciv-l19-29-samson-disappeared",
                "st-chp2-seciv-l19-29-triumph-evaluation",
            ],
            "true": ["st-chp2-seciv-l19-29-committee-lists-amended", "st-chp2-seciv-l19-29-reassignment-accepted"],
        },
        "new_candidates": 0,
        "new_mentions": 0,
        "new_atomic_statements": [NEW_DISCUSSION_ID],
        "remaining_unset_in_segment": [],
        "source_unchanged": True,
        "updated_note_crosslinks": [CITATION_ID, PRIOR_COMMITTEE_ID],
        "payload_sha256": {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, payload in payloads.items():
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(payload)
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
        written = read_jsonl(paths["book-statements.jsonl"])
        written_by_id = {row["statement_id"]: row for row in written}
        if written_by_id[NEW_DISCUSSION_ID].get("qualifiers", {}).get("relation_candidate") is not False:
            raise SystemExit("committee discussion classification was not persisted")
        if written_by_id["st-chp2-seciv-l19-29-reassignment-accepted"].get("qualifiers", {}).get("relation_candidate") is not True:
            raise SystemExit("proposal acceptance relation candidate was not persisted")
        if PRIOR_COMMITTEE_ID not in written_by_id[CITATION_ID].get("qualifiers", {}).get("linked_body_statement_ids", []):
            raise SystemExit("note citation linkage to the prior committee statement was not persisted")
        if digest(SOURCE) != SOURCE_SHA:
            raise SystemExit("source asset changed during write")
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        raise
    print(json.dumps({
        "result": "applied",
        "backups": {name: backup.name for name, backup in backups.items()},
        "written_hashes": {name: digest(path) for name, path in paths.items()},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
