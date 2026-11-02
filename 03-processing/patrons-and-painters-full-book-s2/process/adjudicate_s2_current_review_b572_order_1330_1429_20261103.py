#!/usr/bin/env python3
"""Resolve the p.25 n.4 plural antecedent in S2 batch B572."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ROSTER_PATH = PROCESS / "s2-current-review-roster.csv"
COVERAGE_PATH = TABLES / "s2-coverage.csv"
HISTORY_PATH = PROCESS / "s2-history-9622-review-events.csv"
MENTIONS_PATH = TABLES / "mentions.csv"
SEGMENTS_PATH = TABLES / "segments.jsonl"
ALIGNMENT_PATH = TABLES / "alignment.csv"
RELATIONS_PATH = TABLES / "relations.csv"

BASE_HEAD = "3c885c24f7e8cb09c029bcb773357c1e0dc35f43"
HISTORY_SHA256 = "75ab12df478a816035929353565b0301d55959c6bb13d9b511af072c4c931c89"
SOURCE_HASHES = {
    "02-sources/01-book/CHP-2.pdf": "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e",
    "02-sources/02-Markdown/02_CHP-2_sec_i.md": "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
}
BATCH_ID = "S2-B572-CH2-P25-NOTE4"
STAGE_ID = "2026-11-03-s2-current-review-b572-order-1330-1429-pronoun-scope"
EVIDENCE_REF = f"stages.md#{STAGE_ID}"
NEW_STATEMENTS = {
    "st-chp2-seci-l124-157-albani-study-bacchus": {
        "template": "st-chp2-seci-l124-157-albani-study-andrians",
        "object_candidate_id": "cand-4250",
        "claim": (
            "Haskell’s footnote says Albani must have studied Bacchus and Ariadne, one of the "
            "three Titian paintings named immediately before the note, when he came to Rome in 1601–1602."
        ),
        "qualification": (
            "‘Must have’ marks Haskell’s inference, not an established encounter. The pronoun ‘them’ "
            "resolves to the three Titian paintings named in the printed p.25 body; this row records "
            "the Bacchus and Ariadne member."
        ),
        "relation_candidate_note": (
            "The antecedent of ‘them’ is the three Titian paintings named on printed p.25. This row "
            "records the Albani-study inference for Bacchus and Ariadne (cand-4250), linked to "
            "st-chp2-seci-l44-53-bacchus-transfer. Preserve ‘must have’ as Haskell’s inference; "
            "no formal S6 edge is asserted."
        ),
    },
    "st-chp2-seci-l124-157-darpino-copy-bacchus": {
        "template": "st-chp2-seci-l124-157-darpino-copy-andrians",
        "object_candidate_id": "cand-4250",
        "claim": (
            "Haskell’s footnote reports that Cavaliere d’Arpino copied Bacchus and Ariadne, one of "
            "the three Titian paintings named immediately before the note."
        ),
        "qualification": (
            "The pronoun ‘them’ resolves to the three Titian paintings named in the printed p.25 body. "
            "The note cites a manuscript note in Baglione, p.372, which has not been independently examined; "
            "retain this as Haskell’s report."
        ),
        "relation_candidate_note": (
            "The antecedent of ‘them’ is the three Titian paintings named on printed p.25. This row "
            "records the reported d’Arpino-copy claim for Bacchus and Ariadne (cand-4250), linked to "
            "st-chp2-seci-l44-53-bacchus-transfer. The Baglione manuscript is not independently examined; "
            "no formal S6 edge is asserted."
        ),
    },
}
PENDING_TO_PASS = {
    "st-chp2-seci-l124-157-albani-study-andrians",
    "st-chp2-seci-l124-157-albani-study-worship",
    "st-chp2-seci-l124-157-darpino-copy-andrians",
    "st-chp2-seci-l124-157-darpino-copy-worship",
}
EXPECTED_PENDING = {
    "st-chp2-seci-l95-106-venetian-collection",
    "st-chp2-seci-l95-106-citation-brugnoli-castello",
    "st-chp2-seci-l95-106-citation-brugnoli-frescoes",
    "st-chp2-seci-l95-106-citation-toesca",
    "st-chp2-seci-l108-119-attention-focused-on-reformers",
    "st-chp2-seci-l108-119-old-master-paintings-location",
    "st-chp2-seci-l124-157-rubens-version-andrians",
    "st-chp2-seci-l124-157-rubens-version-worship",
    "st-chp2-seci-l124-157-cite-ortolani",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: object) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                              separators=(",", ":")).encode("utf-8"))


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def read_jsonl(path: Path) -> tuple[list[dict], bytes, str, bool]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    return ([json.loads(line) for line in text.splitlines() if line.strip()], raw,
            "\r\n" if "\r\n" in text else "\n", raw.startswith(b"\xef\xbb\xbf"))


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str], bytes, str, bool]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return (list(reader), list(reader.fieldnames or []), raw,
            "\r\n" if "\r\n" in text else "\n", raw.startswith(b"\xef\xbb\xbf"))


def write_csv(rows: list[dict[str, str]], fields: list[str], newline: str,
              bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline,
                            extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + stream.getvalue().encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expect-plan", default="")
    args = parser.parse_args()

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                   text=True).strip()
    require(head == BASE_HEAD, f"Expected base HEAD {BASE_HEAD}; found {head}")
    for rel, expected in SOURCE_HASHES.items():
        require(sha256((ROOT / rel).read_bytes()) == expected,
                f"Source fingerprint changed: {rel}")
    require(sha256(HISTORY_PATH.read_bytes()) == HISTORY_SHA256,
            "Immutable H9622 review-event ledger changed")

    statements, statements_raw, statements_eol, statements_bom = read_jsonl(STATEMENTS_PATH)
    roster, roster_fields, _, roster_eol, roster_bom = read_csv(ROSTER_PATH)
    segments, _, _, _ = read_jsonl(SEGMENTS_PATH)
    mentions, _, _, _, _ = read_csv(MENTIONS_PATH)
    coverage, coverage_fields, _, coverage_eol, coverage_bom = read_csv(COVERAGE_PATH)
    alignment, _, alignment_raw, _, _ = read_csv(ALIGNMENT_PATH)
    relations, _, relations_raw, _, _ = read_csv(RELATIONS_PATH)

    statement_by_id = {x["statement_id"]: x for x in statements}
    roster_by_id = {x["statement_id"]: x for x in roster}
    require(len(statements) == len(roster) == 15512,
            "Unexpected pre-stage statement/roster size")
    require(len(statement_by_id) == len(statements) and len(roster_by_id) == len(roster),
            "Duplicate statement/roster ID")
    require(set(statement_by_id) == set(roster_by_id),
            "Pre-stage statement and roster ID sets differ")
    require(not any(r["review_batch_id"] == BATCH_ID for r in roster),
            "B572 is already applied")
    for r in roster:
        require(r["current_statement_sha256"] == canonical_hash(statement_by_id[r["statement_id"]]),
                f"Current statement fingerprint mismatch: {r['statement_id']}")

    ordered_old = sorted(roster, key=lambda r: int(r["current_order"]))
    require([int(r["current_order"]) for r in ordered_old] == list(range(1, 15513)),
            "Pre-stage source-order roster is not continuous")
    selected = [r for r in ordered_old if 1330 <= int(r["current_order"]) <= 1429]
    require(len(selected) == 100, "Expected exactly 100 original source-order rows")
    require(sum(r["current_review_status"] == "reviewed_current_pass" for r in selected) == 87,
            "The reusable PASS count changed")
    pending_ids = {r["statement_id"] for r in selected
                   if r["current_review_status"] == "reviewed_current_pending"}
    require(pending_ids == PENDING_TO_PASS | EXPECTED_PENDING,
            f"Unexpected pending set: {sorted(pending_ids)}")
    require(all(r["current_review_status"] in {"reviewed_current_pass", "reviewed_current_pending"}
                for r in selected), "Unexpected current review status in selected rows")

    statement_by_id_after = deepcopy(statement_by_id)
    expected_quote = statement_by_id[
        "st-chp2-seci-l124-157-albani-study-andrians"]["original_quote"]
    for sid, spec in NEW_STATEMENTS.items():
        template = statement_by_id[spec["template"]]
        new = deepcopy(template)
        new["statement_id"] = sid
        new["object_candidate_id"] = spec["object_candidate_id"]
        new["original_quote"] = expected_quote
        q = new["qualifiers"]
        q["claim"] = spec["claim"]
        q["qualification"] = spec["qualification"]
        q["relation_candidate_note"] = spec["relation_candidate_note"]
        q["mentioned_candidate_ids"] = [new["subject_candidate_id"], spec["object_candidate_id"]]
        statement_by_id_after[sid] = new
    bacchus_body_id = "st-chp2-seci-l44-53-bacchus-transfer"
    require(bacchus_body_id in statement_by_id
            and statement_by_id[bacchus_body_id]["subject_candidate_id"] == "cand-4250",
            "The p.25 Bacchus and Ariadne body antecedent is missing or changed")
    require(any(m["segment_id"] == "chp-2:02_CHP-2_sec_i:l44-53"
                and m["candidate_id"] == "cand-4250"
                and m["surface_form"] == "Bacchus and Ariadne" for m in mentions),
            "The printed-p.25 antecedent mention mapping is missing")
    for sid in ("st-chp2-seci-l124-157-albani-study-andrians",
                "st-chp2-seci-l124-157-albani-study-worship",
                "st-chp2-seci-l124-157-darpino-copy-andrians",
                "st-chp2-seci-l124-157-darpino-copy-worship"):
        require(bacchus_body_id in statement_by_id[sid]["qualifiers"]["linked_body_statement_ids"],
                f"The source antecedent link is missing from {sid}")

    # Preserve the established roster sequence, inserting each new same-line claim
    # next to its corresponding per-work statement rather than rebuilding history.
    ordered_ids = [r["statement_id"] for r in ordered_old]
    insert_after = {
        "st-chp2-seci-l124-157-albani-study-worship":
            "st-chp2-seci-l124-157-albani-study-bacchus",
        "st-chp2-seci-l124-157-darpino-copy-worship":
            "st-chp2-seci-l124-157-darpino-copy-bacchus",
    }
    for anchor, new_id in insert_after.items():
        require(anchor in ordered_ids, f"Missing insertion anchor {anchor}")
        ordered_ids.insert(ordered_ids.index(anchor) + 1, new_id)
    require(set(ordered_ids) == set(statement_by_id_after)
            and len(ordered_ids) == 15514, "Post-stage statement order is incomplete")

    segment_by_id = {x["segment_id"]: x for x in segments}
    mentions_by_segment: dict[str, list[dict[str, str]]] = defaultdict(list)
    for m in mentions:
        mentions_by_segment[m["segment_id"]].append(m)
    selected_ids = {r["statement_id"] for r in selected}
    new_roster_by_id = {r["statement_id"]: dict(r) for r in roster}
    template_rows = {
        sid: roster_by_id[spec["template"]] for sid, spec in NEW_STATEMENTS.items()
    }
    for sid, spec in NEW_STATEMENTS.items():
        template_row = template_rows[sid]
        new_row = dict(template_row)
        statement = statement_by_id_after[sid]
        new_row.update({
            "statement_id": sid,
            "snapshot_statement_sha256": "",
            "current_statement_sha256": canonical_hash(statement),
            "history_9622_membership": "not_in_reconstructed_count",
            "prior_review_match": "no_exact_review_mapping",
            "prior_review_ref": "",
            "current_review_status": "reviewed_current_pass",
            "review_batch_id": BATCH_ID,
            "review_outcome": "new_statement_semantic_pass_after_printed_page_review",
            "review_evidence_ref": EVIDENCE_REF,
            "follow_up_note": (
                "B572: New per-work assertion from printed p.25 n.4; ‘them’ resolves to the three "
                "Titian paintings in the linked p.25 body statements. The claim preserves Haskell’s "
                "inference/report and does not create a formal S6 edge."
            ),
            "history_9622_event_count": "0",
            "history_9622_latest_review_commit": "",
            "history_9622_latest_statement_sha256": "",
            "history_9622_current_statement_match": "",
            "history_9622_source_match": "",
            "history_9622_mention_delta": "",
            "history_9622_evidence_ref": "",
        })
        segment = segment_by_id[statement["segment_id"]]
        neighbor = template_row
        new_row.update({
            "chapter": segment["chapter"],
            "section": segment["section"],
            "source_id": segment["source_id"],
            "source_file": segment["source_file"],
            "segment_id": statement["segment_id"],
            "source_line_start": str(statement["qualifiers"]["source_line_start"]),
            "source_line_end": str(statement["qualifiers"]["source_line_end"]),
            "segment_sha256": segment["sha256"],
            "source_asset_sha256": segment.get("asset_sha256", ""),
            "current_segment_mention_count": str(len(mentions_by_segment[statement["segment_id"]])),
        })
        new_roster_by_id[sid] = new_row

    for new_order, sid in enumerate(ordered_ids, start=1):
        row = new_roster_by_id[sid]
        row["current_order"] = str(new_order)
        if sid not in selected_ids and sid not in NEW_STATEMENTS:
            continue
        prior_ref = row.get("review_evidence_ref", "")
        if sid in selected_ids:
            row["review_batch_id"] = BATCH_ID
            row["review_evidence_ref"] = EVIDENCE_REF
            if sid in PENDING_TO_PASS:
                row["current_review_status"] = "reviewed_current_pass"
                row["review_outcome"] = "current_statement_semantic_pass_after_pronoun_scope_resolution"
                detail = (
                    "Printed p.25 n.4 was checked against the adjacent body scan: both ‘them’ "
                    "pronouns refer to the three named Titian paintings. The two Bacchus and Ariadne "
                    "claims are now separately represented; this per-work claim is source-faithful."
                )
            elif row["current_review_status"] == "reviewed_current_pass":
                row["review_outcome"] = "reused_current_pass_after_full_stage_fingerprint_check"
                detail = "Existing current PASS reused after ID, statement, source, segment, and mention fingerprint checks."
            else:
                row["review_outcome"] = "current_pending_retained_after_current_source_and_finding_review"
                detail = "Prior printed-page evidence and current fingerprints agree; the identity, endpoint, or citation finding remains open."
            row["follow_up_note"] = (
                f"B572: {detail} Prior current evidence: {prior_ref}.\n"
                + row.get("follow_up_note", "")
            ).strip()

    # New rows inherit immutable source/mention snapshot hashes from their same-segment
    # templates; the current mention set itself is unchanged.
    for sid, spec in NEW_STATEMENTS.items():
        row = new_roster_by_id[sid]
        template = template_rows[sid]
        row["snapshot_commit"] = template["snapshot_commit"]
        row["snapshot_segment_mention_count"] = template["snapshot_segment_mention_count"]
        row["snapshot_segment_mentions_sha256"] = template["snapshot_segment_mentions_sha256"]
        row["current_segment_mentions_sha256"] = template["current_segment_mentions_sha256"]

    after_roster = [new_roster_by_id[sid] for sid in ordered_ids]
    require([int(r["current_order"]) for r in after_roster] == list(range(1, 15515)),
            "Post-stage source-order roster is not continuous")
    require(set(r["statement_id"] for r in after_roster) == set(statement_by_id_after),
            "Post-stage roster and statement ID sets differ")
    for row in after_roster:
        require(row["current_statement_sha256"] == canonical_hash(statement_by_id_after[row["statement_id"]]),
                f"Post-stage statement fingerprint mismatch: {row['statement_id']}")
    for sid in NEW_STATEMENTS:
        require(new_roster_by_id[sid]["history_9622_event_count"] == "0",
                f"A new statement was incorrectly given a historical event: {sid}")

    status_counts = Counter(r["current_review_status"] for r in after_roster)
    require(status_counts["reviewed_current_pass"] == 8715
            and status_counts["reviewed_current_pending"] == 6799,
            f"Unexpected post-stage status totals: {status_counts}")
    require(sum(int(r["history_9622_event_count"] or "0") for r in after_roster) == 9620,
            "H9622 event-to-current mapping total changed")
    require(sha256(HISTORY_PATH.read_bytes()) == HISTORY_SHA256,
            "Immutable H9622 event ledger changed")

    # Add the adjudication result to the existing S2 segment coverage note.
    target_coverage = [r for r in coverage
                       if r["segment_id"] == "chp-2:02_CHP-2_sec_i:l124-157"]
    require(len(target_coverage) == 1, "Expected one coverage row for p.25 n.4")
    coverage_row = target_coverage[0]
    coverage_suffix = (
        " B572 p.25 n.4: the two instances of ‘them’ resolve to the three Titian paintings "
        "named in the adjacent printed p.25 body; added separate Albani-study and d’Arpino-copy "
        "statements for Bacchus and Ariadne. No named-title mention span was fabricated for the pronoun; "
        "the antecedent is traced through the linked body statements."
    )
    if "B572 p.25 n.4:" not in coverage_row["note"]:
        coverage_row["note"] = coverage_row["note"].rstrip() + coverage_suffix

    append_prefix = b"" if statements_raw.endswith((b"\n", b"\r")) else statements_eol.encode("ascii")
    statement_output = statements_raw + append_prefix + "".join(
        json.dumps(statement_by_id_after[sid], ensure_ascii=False, separators=(",", ":"))
        + statements_eol for sid in NEW_STATEMENTS
    ).encode("utf-8")
    roster_output = write_csv(after_roster, roster_fields, roster_eol, roster_bom)
    coverage_output = write_csv(coverage, coverage_fields, coverage_eol, coverage_bom)
    current_mentions_hashes = {r["segment_id"]: r["current_segment_mentions_sha256"] for r in roster}
    require(all(current_mentions_hashes[r["segment_id"]] == r["current_segment_mentions_sha256"]
                for r in after_roster if r["statement_id"] in roster_by_id),
            "A pre-existing segment mention fingerprint changed")
    require(sha256(ALIGNMENT_PATH.read_bytes()) == sha256(alignment_raw),
            "S3 alignment input changed unexpectedly")
    require(sha256(RELATIONS_PATH.read_bytes()) == sha256(relations_raw),
            "S6 relations input changed unexpectedly")

    plan = {
        "base_head": BASE_HEAD,
        "batch_id": BATCH_ID,
        "baseline_order": [1330, 1429],
        "selected_ids": [r["statement_id"] for r in selected],
        "resolved_current_pending": sorted(PENDING_TO_PASS),
        "new_statement_ids": list(NEW_STATEMENTS),
        "retained_pending_ids": sorted(EXPECTED_PENDING),
        "post_status_counts": dict(status_counts),
        "statement_output_sha256": sha256(statement_output),
        "roster_output_sha256": sha256(roster_output),
        "coverage_output_sha256": sha256(coverage_output),
        "history_ledger_sha256": HISTORY_SHA256,
        "alignment_sha256": sha256(alignment_raw),
        "relations_sha256": sha256(relations_raw),
    }
    plan_hash = canonical_hash(plan)
    print(f"plan_sha256={plan_hash}")
    print("original_rows=100; reused_pass=87; resolved_pending=4; retained_pending=9")
    print("new_statement_rows=2; post_stage_pass=8715; post_stage_pending=6799; total=15514")
    print("h9622_history_ledger=unchanged; relations=unchanged; alignment=unchanged; mention_rows=unchanged")

    if args.apply:
        require(args.expect_plan == plan_hash,
                f"Plan hash mismatch: expected {args.expect_plan!r}, current {plan_hash}")
        STATEMENTS_PATH.write_bytes(statement_output)
        ROSTER_PATH.write_bytes(roster_output)
        COVERAGE_PATH.write_bytes(coverage_output)
        require(sha256(HISTORY_PATH.read_bytes()) == HISTORY_SHA256,
                "Immutable H9622 ledger changed after apply")
        print("applied=true")
    else:
        print("applied=false")


if __name__ == "__main__":
    main()
