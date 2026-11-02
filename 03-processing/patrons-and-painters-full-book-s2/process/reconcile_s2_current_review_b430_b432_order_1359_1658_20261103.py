#!/usr/bin/env python3
"""Reconcile S2 current-review stage B430-B432 after guarded fingerprint checks."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process"
ROSTER_PATH = PROCESS / "s2-current-review-roster.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
SEGMENTS_PATH = TABLES / "segments.jsonl"
MENTIONS_PATH = TABLES / "mentions.csv"
HISTORY_PATH = PROCESS / "s2-history-9622-review-events.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
RELATIONS_PATH = TABLES / "relations.csv"

BASE_HEAD = "9da6b361584561097978cac6fe504d1ace84378d"
HISTORY_SHA256 = "75ab12df478a816035929353565b0301d55959c6bb13d9b511af072c4c931c89"
BATCH_ID = "S2-B430-B432-CH2-1359-1658"
STAGE_ID = "2026-11-03-s2-current-review-stage-b430-b432-order-1359-1658"
EVIDENCE_REF = f"stages.md#{STAGE_ID}"
SOURCE_HASHES = {
    "02-sources/01-book/CHP-2.pdf": "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e",
    "02-sources/02-Markdown/02_CHP-2_sec_i.md": "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
    "02-sources/02-Markdown/02_CHP-2_sec_i_visual-transcription.md": "6cb9a15d372adec12c6ff34283991fdbfb6d62f9d326240c5624b26636ab3fa9",
    "02-sources/02-Markdown/02_CHP-2_sec_i_plate3_visual-transcription.md": "c35feb7762a65ac277d6b9b7df265bcc47c9ad8fb5748cc540d1fbcf8a59aee5",
    "02-sources/02-Markdown/02_CHP-2_sec_ii.md": "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9",
}
CHUNKS = ((1359, 1458), (1459, 1558), (1559, 1658))
EXPECTED_HASH_CHANGED = {
    "st-chp2-seci-l124-157-giustiniani-friend-bizoni",
    "st-chp2-secii-l52-60-programme-duration",
    "st-chp2-secii-l62-69-berninimade-bibiana-statue",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: object) -> str:
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines()
            if line.strip()]


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str], str, bool]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    rows = list(reader)
    fields = list(reader.fieldnames or [])
    first_lf = raw.find(b"\n")
    newline = "\r\n" if first_lf > 0 and raw[first_lf - 1:first_lf] == b"\r" else "\n"
    return rows, fields, newline, raw.startswith(b"\xef\xbb\xbf")


def write_csv(rows: list[dict[str, str]], fields: list[str], newline: str,
              bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline,
                            extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    prefix = b"\xef\xbb\xbf" if bom else b""
    return prefix + stream.getvalue().encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expect-plan", default="")
    args = parser.parse_args()

    require(__import__("subprocess").check_output(["git", "rev-parse", "HEAD"],
            cwd=ROOT, text=True).strip() == BASE_HEAD, "Unexpected base HEAD")
    for relative, expected in SOURCE_HASHES.items():
        require(digest((ROOT / relative).read_bytes()) == expected,
                f"Source fingerprint changed: {relative}")
    history_raw = HISTORY_PATH.read_bytes()
    require(digest(history_raw) == HISTORY_SHA256, "Immutable H9622 ledger changed")

    roster, fields, newline, bom = read_csv(ROSTER_PATH)
    statements = read_jsonl(STATEMENTS_PATH)
    segments = read_jsonl(SEGMENTS_PATH)
    mentions, _, _, _ = read_csv(MENTIONS_PATH)
    statement_by_id = {row["statement_id"]: row for row in statements}
    segment_by_id = {row["segment_id"]: row for row in segments}
    roster_by_id = {row["statement_id"]: row for row in roster}
    mentions_by_segment: dict[str, list[dict[str, str]]] = defaultdict(list)
    for mention in mentions:
        mentions_by_segment[mention["segment_id"]].append(mention)

    require(len(roster) == len(statements) == 15512, "Unexpected statement/roster count")
    require(len(roster_by_id) == len(roster) == len(statement_by_id), "Duplicate statement ID")
    require(set(roster_by_id) == set(statement_by_id), "Statement ID sets differ")
    selected = sorted((r for r in roster if 1359 <= int(r["current_order"]) <= 1658),
                      key=lambda r: int(r["current_order"]))
    require(len(selected) == 300, f"Expected 300 rows, found {len(selected)}")
    require([int(r["current_order"]) for r in selected] == list(range(1359, 1659)),
            "Selected interval is not continuous")
    require(not any(r["review_batch_id"] == BATCH_ID for r in roster),
            "Stage has already been applied")

    fingerprint_errors: list[str] = []
    for row in selected:
        sid = row["statement_id"]
        if row["current_statement_sha256"] != canonical_hash(statement_by_id[sid]):
            fingerprint_errors.append(f"statement:{sid}")
        segment = segment_by_id[row["segment_id"]]
        if row["segment_sha256"] != segment["sha256"]:
            fingerprint_errors.append(f"segment:{row['segment_id']}")
        if row["source_asset_sha256"] != segment.get("asset_sha256", ""):
            fingerprint_errors.append(f"segment-asset:{row['segment_id']}")
        if digest((ROOT / row["source_file"]).read_bytes()) != row["source_asset_sha256"]:
            fingerprint_errors.append(f"source-file:{row['source_file']}")
        segment_mentions = sorted(mentions_by_segment[row["segment_id"]],
                                  key=lambda item: item["mention_id"])
        if len(segment_mentions) != int(row["current_segment_mention_count"]):
            fingerprint_errors.append(f"mention-count:{row['segment_id']}")
        if canonical_hash(segment_mentions) != row["current_segment_mentions_sha256"]:
            fingerprint_errors.append(f"mentions:{row['segment_id']}")
        require(bool(row["review_evidence_ref"]), f"Missing prior evidence: {sid}")
    require(not fingerprint_errors, "Fingerprint errors: " + ", ".join(fingerprint_errors[:10]))

    current_status = Counter(row["current_review_status"] for row in selected)
    require(current_status == {"reviewed_current_pass": 165,
                               "reviewed_current_pending": 135},
            f"Unexpected current status counts: {current_status}")
    for start, end, expected in (
        (1359, 1458, (91, 9, 100, 99, 1, 0)),
        (1459, 1558, (43, 57, 100, 100, 0, 0)),
        (1559, 1658, (31, 69, 96, 94, 2, 4)),
    ):
        chunk = [r for r in selected if start <= int(r["current_order"]) <= end]
        pass_count = sum(r["current_review_status"] == "reviewed_current_pass" for r in chunk)
        pending_count = sum(r["current_review_status"] == "reviewed_current_pending" for r in chunk)
        events = sum(int(r["history_9622_event_count"] or "0") for r in chunk)
        exact = sum(r["history_9622_current_statement_match"] == "exact" for r in chunk)
        changed = sum(r["history_9622_current_statement_match"] == "changed" for r in chunk)
        no_history = sum(r["history_9622_membership"] == "not_in_reconstructed_count" for r in chunk)
        require((pass_count, pending_count, events, exact, changed, no_history) == expected,
                f"Unexpected counts for {start}-{end}")
    require({r["statement_id"] for r in selected
             if r["history_9622_current_statement_match"] == "changed"} == EXPECTED_HASH_CHANGED,
            "Historical statement hash delta IDs changed")
    require(all(r["history_9622_source_match"] == "true" for r in selected
                if int(r["history_9622_event_count"] or "0")),
            "A historical source version mismatch exists")
    require(sum(int(r["history_9622_event_count"] or "0") for r in selected) == 296,
            "Unexpected H9622 event count")

    alignment_raw = ALIGNMENT_PATH.read_bytes()
    relations_raw = RELATIONS_PATH.read_bytes()
    roster_output_rows = [dict(row) for row in roster]
    output_by_id = {row["statement_id"]: row for row in roster_output_rows}
    for row in selected:
        target = output_by_id[row["statement_id"]]
        prior_evidence = row["review_evidence_ref"]
        prior_status = row["current_review_status"]
        target["review_batch_id"] = BATCH_ID
        target["review_evidence_ref"] = EVIDENCE_REF
        target["review_outcome"] = (
            "reused_current_pass_after_full_stage_fingerprint_check"
            if prior_status == "reviewed_current_pass"
            else "current_pending_retained_after_exact_version_and_prior_review_check"
        )
        decision = "复用既有current PASS" if prior_status == "reviewed_current_pass" else "保留既有pending finding"
        target["follow_up_note"] = (
            f"B430–B432整阶段核平：{decision}；当前statement、source asset、segment和mention集合指纹匹配。"
            f"原逐页证据：{prior_evidence}。\n" + target.get("follow_up_note", "")
        ).strip()

    roster_output = write_csv(roster_output_rows, fields, newline, bom)
    global_status = Counter(row["current_review_status"] for row in roster_output_rows)
    require(global_status["reviewed_current_pass"] == 8677 and
            global_status["reviewed_current_pending"] == 6835,
            f"Unexpected global status counts: {global_status}")
    require(digest(HISTORY_PATH.read_bytes()) == HISTORY_SHA256,
            "H9622 ledger changed during plan")

    plan = {
        "base_head": BASE_HEAD,
        "stage_id": STAGE_ID,
        "order": [1359, 1658],
        "selected_ids": [row["statement_id"] for row in selected],
        "fingerprint_errors": fingerprint_errors,
        "reused_pass": current_status["reviewed_current_pass"],
        "retained_pending": current_status["reviewed_current_pending"],
        "history_events": 296,
        "history_exact": 293,
        "history_changed_ids": sorted(EXPECTED_HASH_CHANGED),
        "history_no_prior_event": 4,
        "roster_sha256": digest(ROSTER_PATH.read_bytes()),
        "roster_output_sha256": digest(roster_output),
        "alignment_sha256": digest(alignment_raw),
        "relations_sha256": digest(relations_raw),
        "history_sha256": digest(history_raw),
        "global_status": dict(global_status),
    }
    plan_hash = canonical_hash(plan)
    if args.apply:
        require(args.expect_plan == plan_hash, "Plan hash mismatch")
        temp = ROSTER_PATH.with_suffix(".csv.B430.tmp")
        temp.write_bytes(roster_output)
        temp.replace(ROSTER_PATH)
        print("applied=true")
    else:
        print("applied=false")
    print(f"stage={BATCH_ID}")
    print(f"plan_sha256={plan_hash}")
    print("rows=300; reused_current_pass=165; retained_current_pending=135; newly_pass=0")
    print("H9622_events=296; exact=293; changed=3; no_prior_event=4; source_matches=296/296")
    print("post_current_pass=8677; post_current_pending=6835")
    print(f"alignment_sha256={digest(alignment_raw)}")
    print(f"relations_sha256={digest(relations_raw)}")


if __name__ == "__main__":
    main()
