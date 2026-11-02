#!/usr/bin/env python3
"""Apply S2 batch B429 after fingerprint, source, and plan-hash checks."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ROSTER_PATH = PROCESS / "s2-current-review-roster.csv"
MENTIONS_PATH = TABLES / "mentions.csv"
SEGMENTS_PATH = TABLES / "segments.jsonl"
HISTORY_PATH = PROCESS / "s2-history-9622-review-events.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
RELATIONS_PATH = TABLES / "relations.csv"

BASE_HEAD = "319ac90848afeddfe39e44dabdb6c5ef4ace0fdd"
HISTORY_SHA256 = "75ab12df478a816035929353565b0301d55959c6bb13d9b511af072c4c931c89"
BATCH_ID = "S2-B429-CH2-SECI-1259-1358"
STAGE_ID = "2026-11-03-s2-current-review-b429-order-1259-1358"
EVIDENCE_REF = f"stages.md#{STAGE_ID}"
SOURCE_HASHES = {
    "02-sources/01-book/CHP-2.pdf": "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e",
    "02-sources/02-Markdown/02_CHP-2_sec_i.md": "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
}

PASS_AFTER_REVIEW = {
    "st-chp2-seci-l95-106-cupid-iconography": {
        "claim": (
            "Haskell describes the unidentified painting as showing the winged, yet all-too-human, "
            "Cupid sitting on a rumpled bed and scornfully trampling on the symbols of culture "
            "that Giustiniani was so keenly fostering."
        ),
        "qualification": (
            "The source identifies the represented figure as Cupid and describes the gesture, but "
            "supplies no painting title or artist. Retain the source's stated connection between "
            "the trampled symbols of culture and what Giustiniani was keenly fostering."
        ),
        "relation_candidate": True,
        "relation_candidate_note": (
            "This is a source-reported depiction candidate linking an unidentified painting to its "
            "represented figure. The painting's title and artist remain unresolved; no formal S6 "
            "edge is asserted until the endpoints are registered."
        ),
        "mentioned_candidate_ids": ["cand-4320", "cand-4321", "cand-1200"],
    },
    "st-chp2-seci-l95-106-contrast-fragment": {
        "claim": (
            "Haskell begins a contrast between Giustiniani's taste as revealed in his actual "
            "painting collection and his writings."
        ),
        "qualification": (
            "Printed p.29 L103 ends before the sentence is complete; it continues on printed p.30 "
            "L108–109. Do not infer a conclusion from this fragment; the complete comparison is "
            "recorded in the linked statement."
        ),
        "relation_candidate": False,
        "relation_candidate_note": (
            "This is an authorial comparative transition, not a formal relationship. Its completed "
            "comparison is recorded in the linked continuation statement."
        ),
        "mentioned_candidate_ids": ["cand-1200", "cand-4313"],
        "linked_statement_ids": ["st-chp2-seci-l108-119-taste-more-defined-than-writings"],
    },
    "st-chp2-seci-l95-106-hopf-relevance": {
        "claim": (
            "Haskell says the reported but untraced work by Carlo Hopf was of no importance for "
            "the Marchese Vincenzo."
        ),
        "qualification": (
            "This is Haskell's relevance judgment about the reported work specifically for "
            "Vincenzo Giustiniani, not an objective appraisal of the work's scholarly value. "
            "The work's reported untraceability remains attributed to Haskell."
        ),
        "relation_candidate": False,
        "relation_candidate_note": (
            "Preserve this authorial relevance judgment as narrative content; it is not an "
            "objective fact or a formal S6 relationship."
        ),
        "mentioned_candidate_ids": ["cand-4336", "cand-1200"],
    },
}

PENDING_AFTER_REVIEW = {
    "st-chp2-seci-l95-106-venetian-collection": (
        "Printed p.29 L101–102 names the Venetian High Renaissance masters as painters in the "
        "additional collection group. Keep that collective distinct from term cand-4319 and work "
        "group cand-11568. cand-11569 remains untyped and undecided; no formal creator edge."
    ),
    "st-chp2-seci-l95-106-citation-brugnoli-castello": (
        "Printed p.29 n.5 names M. V. Brugnoli and 1957; the bibliography lists two distinct "
        "Brugnoli articles that year. The note supplies no title, so this candidate target and "
        "rel-1981 remain pending."
    ),
    "st-chp2-seci-l95-106-citation-brugnoli-frescoes": (
        "Printed p.29 n.5 names Brugnoli and 1957; it does not distinguish the two same-author, "
        "same-year bibliography entries. Keep this candidate and rel-1982 pending."
    ),
    "st-chp2-seci-l95-106-citation-toesca": (
        "Printed p.29 n.5 reads I. Toesca, while the p.438 bibliography entry reads L. Toesca. "
        "The title is absent from the note; retain the possible match and rel-1983 as pending."
    ),
    "st-chp2-seci-l108-119-attention-focused-on-reformers": (
        "Printed p.30 L110 names Caravaggio, the Carracci collectively, and their followers. "
        "The full scope is retained in object_candidate_id and other_candidate_ids, but the "
        "collective/follower endpoints are unresolved; do not formalize a partial edge."
    ),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return digest(payload)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def read_jsonl(path: Path) -> tuple[list[dict], list[str], bytes, str]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    rows = [json.loads(line) for line in lines if line.strip()]
    newline = "\r\n" if "\r\n" in text else "\n"
    return rows, lines, raw, newline


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str], bytes, str, bool]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    fields = list(reader.fieldnames or [])
    rows = list(reader)
    first_lf = raw.find(b"\n")
    newline = "\r\n" if first_lf > 0 and raw[first_lf - 1:first_lf] == b"\r" else "\n"
    return rows, fields, raw, newline, raw.startswith(b"\xef\xbb\xbf")


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

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                   text=True).strip()
    require(head == BASE_HEAD, f"Expected base HEAD {BASE_HEAD}; found {head}")
    for relative, expected in SOURCE_HASHES.items():
        require(digest((ROOT / relative).read_bytes()) == expected,
                f"Source fingerprint changed: {relative}")
    require(digest(HISTORY_PATH.read_bytes()) == HISTORY_SHA256,
            "The immutable H9622 event ledger changed")

    statements, statement_lines, statement_raw, statement_eol = read_jsonl(STATEMENTS_PATH)
    segments, _, _, _ = read_jsonl(SEGMENTS_PATH)
    roster, roster_fields, _, roster_eol, roster_bom = read_csv(ROSTER_PATH)
    mentions, _, _, _, _ = read_csv(MENTIONS_PATH)
    alignments, _, alignment_raw, _, _ = read_csv(ALIGNMENT_PATH)
    relations, _, relations_raw, _, _ = read_csv(RELATIONS_PATH)

    statement_by_id = {row["statement_id"]: row for row in statements}
    roster_by_id = {row["statement_id"]: row for row in roster}
    segment_by_id = {row["segment_id"]: row for row in segments}
    require(len(statements) == len(roster) == 15512,
            "Unexpected current statement/roster size")
    require(len(statement_by_id) == len(statements) and
            len(roster_by_id) == len(roster), "Duplicate statement or roster ID")
    require(set(statement_by_id) == set(roster_by_id),
            "Current statement and roster ID sets differ")
    require(not any(row["review_batch_id"] == BATCH_ID for row in roster),
            "B429 has already been applied")
    for row in roster:
        require(row["current_statement_sha256"] ==
                canonical_hash(statement_by_id[row["statement_id"]]),
                f"Current statement hash mismatch: {row['statement_id']}")

    selected = sorted(
        (row for row in roster if 1259 <= int(row["current_order"]) <= 1358),
        key=lambda row: int(row["current_order"]),
    )
    require(len(selected) == 100, f"Expected 100 rows; found {len(selected)}")
    require([int(row["current_order"]) for row in selected] == list(range(1259, 1359)),
            "Selected current-order interval is not continuous")
    pending_ids = {row["statement_id"] for row in selected
                   if row["current_review_status"] == "reviewed_current_pending"}
    require(pending_ids == set(PASS_AFTER_REVIEW) | set(PENDING_AFTER_REVIEW),
            f"Pending set changed: {sorted(pending_ids)}")
    require(sum(row["current_review_status"] == "reviewed_current_pass"
                for row in selected) == 92, "Expected 92 current PASS rows")
    require(sum(int(row["history_9622_event_count"] or "0") for row in selected) == 100,
            "Expected 100 H9622 events in the selected interval")
    require(all(row["history_9622_source_match"] == "true" for row in selected),
            "A selected row has a source version mismatch")

    mentions_by_segment: dict[str, list[dict[str, str]]] = defaultdict(list)
    for mention in mentions:
        mentions_by_segment[mention["segment_id"]].append(mention)
    for row in selected:
        segment = segment_by_id[row["segment_id"]]
        segment_mentions = sorted(mentions_by_segment[row["segment_id"]],
                                  key=lambda item: item["mention_id"])
        require(segment["sha256"] == row["segment_sha256"],
                f"Segment hash mismatch: {row['segment_id']}")
        require(segment.get("asset_sha256", "") == row["source_asset_sha256"],
                f"Source asset hash mismatch in roster: {row['segment_id']}")
        require(len(segment_mentions) == int(row["current_segment_mention_count"]),
                f"Segment mention count mismatch: {row['segment_id']}")
        require(canonical_hash(segment_mentions) == row["current_segment_mentions_sha256"],
                f"Segment mention hash mismatch: {row['segment_id']}")

    alignment_by_candidate = {row["candidate_id"]: row for row in alignments}
    for candidate_id in ("cand-11569", "cand-11568", "cand-4318", "cand-4340",
                         "cand-4320", "cand-4321", "cand-4313", "cand-4336"):
        require(alignment_by_candidate[candidate_id]["decision"] == "undecided",
                f"Unexpected S3 decision for {candidate_id}")
    relation_by_id = {row["relation_id"]: row for row in relations}
    for relation_id in ("rel-1981", "rel-1982", "rel-1983"):
        require(relation_by_id[relation_id]["status"] == "pending",
                f"Unexpected relation decision for {relation_id}")

    before_hashes = {sid: canonical_hash(statement_by_id[sid]) for sid in PASS_AFTER_REVIEW}
    after_statements = json.loads(json.dumps(statements, ensure_ascii=False))
    after_by_id = {row["statement_id"]: row for row in after_statements}
    for sid, patch in PASS_AFTER_REVIEW.items():
        statement = after_by_id[sid]
        qualifiers = statement["qualifiers"]
        qualifiers.update(patch)

    rewritten_lines: list[str] = []
    changed_ids = set(PASS_AFTER_REVIEW)
    for line in statement_lines:
        if not line.strip():
            rewritten_lines.append(line)
            continue
        old = json.loads(line)
        sid = old["statement_id"]
        if sid in changed_ids:
            rewritten_lines.append(json.dumps(after_by_id[sid], ensure_ascii=False,
                                              separators=(",", ":")) + statement_eol)
        else:
            rewritten_lines.append(line)
    statement_output = (
        (b"\xef\xbb\xbf" if statement_raw.startswith(b"\xef\xbb\xbf") else b"")
        + "".join(rewritten_lines).encode("utf-8")
    )

    after_roster = [dict(row) for row in roster]
    after_roster_by_id = {row["statement_id"]: row for row in after_roster}
    for row in selected:
        target = after_roster_by_id[row["statement_id"]]
        prior_evidence = row["review_evidence_ref"]
        target["review_batch_id"] = BATCH_ID
        target["review_evidence_ref"] = EVIDENCE_REF
        if row["statement_id"] in PASS_AFTER_REVIEW:
            target["current_review_status"] = "reviewed_current_pass"
            target["review_outcome"] = "current_semantic_pass_after_printed_page_review"
            detail = "B429原页复核后转当前PASS。"
        elif row["statement_id"] in PENDING_AFTER_REVIEW:
            target["current_review_status"] = "reviewed_current_pending"
            target["review_outcome"] = "current_open_finding_retained_after_printed_page_review"
            detail = PENDING_AFTER_REVIEW[row["statement_id"]]
        else:
            target["review_outcome"] = (
                "reused_current_pass_after_statement_source_and_mention_fingerprint_check"
            )
            detail = "B429核对当前statement、source asset、segment及mention指纹后复用既有PASS。"
        target["follow_up_note"] = (
            f"B429：{detail} 前次依据：{prior_evidence}。\n"
            + target.get("follow_up_note", "")
        ).strip()

    for sid in changed_ids:
        target = after_roster_by_id[sid]
        current_hash = canonical_hash(after_by_id[sid])
        target["current_statement_sha256"] = current_hash
        if int(target["history_9622_event_count"] or "0") > 0:
            target["history_9622_current_statement_match"] = (
                "exact" if target["history_9622_latest_statement_sha256"] == current_hash
                else "changed"
            )
            target["prior_review_match"] = (
                "exact_object_and_source_segment"
                if target["history_9622_current_statement_match"] == "exact"
                and target["history_9622_source_match"] == "true"
                else "historical_object_or_source_differs"
            )

    roster_output = write_csv(after_roster, roster_fields, roster_eol, roster_bom)
    status_counts = Counter(row["current_review_status"] for row in after_roster)
    match_counts = Counter(row["history_9622_current_statement_match"]
                           for row in after_roster if row["history_9622_event_count"])
    require(len(after_roster) == 15512, "B429 unexpectedly changed roster size")
    require(status_counts["reviewed_current_pass"] == 8677 and
            status_counts["reviewed_current_pending"] == 6835,
            f"Unexpected post-batch status counts: {status_counts}")
    require(match_counts["exact"] == 9004 and match_counts["changed"] == 533,
            f"Unexpected post-batch history counts: {match_counts}")
    require(digest(HISTORY_PATH.read_bytes()) == HISTORY_SHA256,
            "Immutable H9622 history changed during planning")

    plan = {
        "base_head": BASE_HEAD,
        "batch_id": BATCH_ID,
        "order": [1259, 1358],
        "selected_ids": [row["statement_id"] for row in selected],
        "changed_statement_ids": sorted(changed_ids),
        "before_statement_hashes": before_hashes,
        "after_statement_hashes": {
            sid: canonical_hash(after_by_id[sid]) for sid in sorted(changed_ids)
        },
        "statement_output_sha256": digest(statement_output),
        "roster_output_sha256": digest(roster_output),
        "post_status_counts": dict(status_counts),
        "post_history_hash_counts": dict(match_counts),
        "alignment_sha256": digest(alignment_raw),
        "relations_sha256": digest(relations_raw),
    }
    plan_hash = canonical_hash(plan)

    if args.apply:
        require(args.expect_plan == plan_hash,
                f"Plan hash mismatch: expected {args.expect_plan!r}, current {plan_hash}")
        STATEMENTS_PATH.write_bytes(statement_output)
        ROSTER_PATH.write_bytes(roster_output)
        require(digest(HISTORY_PATH.read_bytes()) == HISTORY_SHA256,
                "Immutable H9622 history changed after apply")
        require(digest(ALIGNMENT_PATH.read_bytes()) == digest(alignment_raw),
                "S3 alignment table changed during B429")
        require(digest(RELATIONS_PATH.read_bytes()) == digest(relations_raw),
                "S6 relations table changed during B429")
        print("applied=true")
    else:
        print("applied=false")

    print(f"batch={BATCH_ID}")
    print(f"plan_sha256={plan_hash}")
    print("rows=100; reused_current_pass=92; rechecked_pending=8; newly_pass=3; remain_pending=5")
    print("statement_changes=3; mention_changes=0; alignment_changes=0; relation_changes=0")
    print("post_current_pass=8677; post_current_pending=6835")
    print("post_history_statement_hash_exact=9004; changed=533; source_matches=9537/9537")
    print(f"prewrite_alignment_sha256={digest(alignment_raw)}")
    print(f"prewrite_relations_sha256={digest(relations_raw)}")


if __name__ == "__main__":
    main()
