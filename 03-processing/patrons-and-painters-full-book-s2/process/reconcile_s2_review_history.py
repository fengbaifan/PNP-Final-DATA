#!/usr/bin/env python3
"""Reconstruct the 9,622 counted S2 review events, without granting acceptance."""

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
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process"
TABLES = ROOT / "04-knowledge/tables"
ROSTER = PROCESS / "s2-current-review-roster.csv"
LEDGER = PROCESS / "s2-history-9622-review-events.csv"
RELATIVE_LEDGER = LEDGER.relative_to(ROOT).as_posix()
REPORT = "03-processing/patrons-and-painters-full-book-s2/process/"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def git_text(revision: str, path: str) -> str:
    return subprocess.check_output(["git", "show", f"{revision}:{path}"],
                                   cwd=ROOT).decode("utf-8-sig")


def chapter(row: dict) -> str:
    return row["segment_id"].split(":", 1)[0]


def page(row: dict) -> str:
    q = row["qualifiers"]
    return str(q.get("print_page") or q.get("printed_page") or "")


def snapshot(revision: str) -> dict:
    full_revision = subprocess.check_output(["git", "rev-parse", revision],
                                            cwd=ROOT, text=True).strip()
    rows = [json.loads(s) for s in git_text(revision, "04-knowledge/tables/book-statements.jsonl").splitlines() if s]
    segments = {s["segment_id"]: s for s in
                (json.loads(s) for s in git_text(revision, "04-knowledge/tables/segments.jsonl").splitlines() if s)}
    mentions = defaultdict(dict)
    for m in csv.DictReader(io.StringIO(git_text(revision, "04-knowledge/tables/mentions.csv"))):
        mentions[m["segment_id"]][m["mention_id"]] = m
    blobs = {}
    tree = subprocess.check_output(["git", "ls-tree", "-r", revision, "--",
                                    "02-sources/01-book", "02-sources/02-Markdown"], cwd=ROOT).decode("utf-8")
    for line in tree.splitlines():
        meta, path = line.split("\t", 1)
        blobs[path] = meta.split()[2]
    return {"revision": full_revision, "rows": rows, "segments": segments,
            "mentions": mentions, "blobs": blobs, "context_cache": {}}


def csv_bytes(rows: list[dict], fields: list[str]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return b"\xef\xbb\xbf" + buffer.getvalue().encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expect-plan", default="")
    args = parser.parse_args()
    current = snapshot("HEAD")
    working = [json.loads(s) for s in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if s]
    if working != current["rows"]:
        raise SystemExit("Commit current statement edits before reconstructing historical evidence")
    current_by_id = {r["statement_id"]: r for r in working}
    current_hashes = {sid: digest(r) for sid, r in current_by_id.items()}
    with ROSTER.open(encoding="utf-8-sig", newline="") as stream:
        roster = list(csv.DictReader(stream))
    assert len(roster) == len(current_by_id) == len({r["statement_id"] for r in roster})
    assert {r["statement_id"] for r in roster} == set(current_by_id)
    assert all(r["current_statement_sha256"] == current_hashes[r["statement_id"]] for r in roster)

    events: list[dict] = []
    batches: list[dict] = []
    seen: set[str] = set()

    def add(batch: str, snap: dict, selected: list[dict], expected: int,
            evidence: str, evidence_revision: str | None = None) -> None:
        assert len(selected) == expected, (batch, len(selected), expected)
        assert len({r["statement_id"] for r in selected}) == expected
        repeated = sum(r["statement_id"] in seen for r in selected)
        for row in sorted(selected, key=lambda r: r["statement_id"]):
            sid, segid = row["statement_id"], row["segment_id"]
            old_segment = snap["segments"][segid]
            now_segment = current["segments"].get(segid, {})
            if segid not in snap["context_cache"]:
                old_m, now_m = snap["mentions"].get(segid, {}), current["mentions"].get(segid, {})
                changed = sorted(k for k in old_m.keys() & now_m.keys() if old_m[k] != now_m[k])
                removed, added = sorted(old_m.keys() - now_m.keys()), sorted(now_m.keys() - old_m.keys())
                mention_delta = {"changed": changed, "removed": removed, "added": added}
                same_segment = all(old_segment.get(k) == now_segment.get(k) for k in
                                   ("source_id", "source_file", "sha256", "asset_sha256"))
                source_file = old_segment["source_file"]
                same_file = snap["blobs"].get(source_file) == current["blobs"].get(source_file)
                number = chapter(row).split("-")[-1]
                suffix = "18Conclusion" if number == "18" else "19Appendix" if number == "19" else number
                pdf = f"02-sources/01-book/CHP-{suffix}.pdf"
                same_pdf = bool(snap["blobs"].get(pdf)) and snap["blobs"].get(pdf) == current["blobs"].get(pdf)
                snap["context_cache"][segid] = {
                    "source_match": same_segment and same_file and same_pdf,
                    "mention_hash": digest(sorted(old_m.values(), key=lambda m: m["mention_id"])),
                    "mention_delta": json.dumps(mention_delta, ensure_ascii=False, separators=(",", ":")),
                }
            context = snap["context_cache"][segid]
            old_hash = digest(row)
            match = "absent_current" if sid not in current_by_id else "exact" if old_hash == current_hashes[sid] else "changed"
            events.append({
                "history_event_id": f"H9622-{len(events)+1:05d}",
                "count_batch_id": batch,
                "statement_id": sid,
                "repeats_prior_id": str(sid in seen).lower(),
                "review_snapshot_commit": snap["revision"],
                "review_statement_sha256": old_hash,
                "segment_id": segid,
                "review_segment_sha256": old_segment["sha256"],
                "review_source_asset_sha256": old_segment["asset_sha256"],
                "review_segment_mentions_sha256": context["mention_hash"],
                "review_evidence_ref": evidence,
                "review_evidence_commit": evidence_revision or snap["revision"],
                "historical_outcome": "directly_read_with_open_findings_unless_separate_pass_record",
                "current_statement_sha256": current_hashes.get(sid, ""),
                "current_statement_match": match,
                "current_source_match": str(context["source_match"]).lower(),
                "mention_delta": context["mention_delta"],
            })
            seen.add(sid)
        batches.append({"batch": batch, "counted_events": expected, "repeated_prior_ids": repeated})

    base = snapshot("2273e274")
    whole_counts = {"chp-1": 521, "chp-2": 1441, "chp-4": 1082, "chp-5": 1073,
                    "chp-6": 763, "chp-9": 904, "chp-13": 579, "chp-14": 502,
                    "chp-15": 551, "chp-16": 206, "chp-17": 142, "chp-18": 24, "chp-19": 116}
    for ch, count in whole_counts.items():
        name = "s2-independent-review-chp1-2-4-20261020.md" if ch in {"chp-1", "chp-2", "chp-4"} else "s2-independent-review-chp13-17-20261020.md" if int(ch.split("-")[1]) >= 13 else "stages.md"
        add("H9258-" + ch, base, [r for r in base["rows"] if chapter(r) == ch], count,
            REPORT + name + "; scope=full " + ch)
    early = {"chp-7:07_CHP-7_intro:l11-15", *["chp-7:07_CHP-7_sec_i:" + s for s in
             ("l3-9", "l11-19", "l21-29", "l31-35", "l37-43", "l45-59", "l61-74", "l76-89")]}
    add("H9258-chp-7-through-p196", base,
        [r for r in base["rows"] if chapter(r) == "chp-7" and
         (r["segment_id"] in early or page(r).isdigit() and 177 <= int(page(r)) <= 196)],
        937, REPORT + "stages.md; scope=2026-10-20 chapter 7 p169-p196; early footnotes and plates excluded unless explicitly reviewed")
    add("H9258-chp-8-non-sec-ii", base,
        [r for r in base["rows"] if chapter(r) == "chp-8" and not r["source_file"].endswith("/08_CHP-8_sec_ii.md")],
        417, REPORT + "stages.md; scope=2026-10-20 chapter 8 non-sec-ii batches 1-411 plus six visual rows")
    assert len(events) == 9258
    extra = [
        ("H9400-chp7-p197", lambda r: chapter(r) == "chp-7" and page(r) == "197", 46),
        ("H9400-chp7-p198-body", lambda r: r["segment_id"] == "chp-7:07_CHP-7_sec_iv:l77-87", 25),
        ("H9400-chp8-p215-body", lambda r: r["segment_id"] == "chp-8:08_CHP-8_sec_ii:l11-19", 29),
        ("H9400-chp8-p216", lambda r: chapter(r) == "chp-8" and page(r) == "216", 30),
        ("H9400-chp8-plate33", lambda r: r["segment_id"] == "chp-8:08_CHP-8_sec_ii:l37-39", 6),
        ("H9400-chp8-plate34-35a", lambda r: r["segment_id"] in {"chp-8:08_CHP-8_sec_ii:l41-43", "chp-8:08_CHP-8_sec_ii:l45-46"}, 5),
    ]
    for name, selector, count in extra:
        add(name, base, [r for r in base["rows"] if selector(r)], count,
            REPORT + "stages.md; scope=" + name + "; statement version before documented post-review repairs", "de818927")
    del base
    later = snapshot("79f22641")
    add("H9400-chp7-p195-new-citation", later,
        [r for r in later["rows"] if r["statement_id"] == "st-chp7-p195-n1-wilhelm-citation"],
        1, REPORT + "stages.md#s2-split-wilhelm-citation-and-p195-comment-20261020")
    del later
    assert len(events) == 9400
    increments = [
        ("d75d5c4d", "chp-7:07_CHP-7_sec_v:l3-7", 14),
        ("de2ac92e", "chp-7:07_CHP-7_sec_v:l9-18", 32),
        ("3ec70ba7", None, 6),
        ("1fb32209", "chp-7:07_CHP-7_sec_v:l42-55", 38),
        ("2a6f8c82", "chp-7:07_CHP-7_sec_v:l57-60", 13),
        ("43499bc8", "chp-7:07_CHP-7_sec_v:l62-76", 34),
        ("bfc87028", "chp-5:05_CHP-5_sec_iii:l82-93", 36),
    ]
    for revision, segment, count in increments:
        snap = snapshot(revision)
        selected = [r for r in snap["rows"] if r["segment_id"] == segment] if segment else [r for r in snap["rows"] if r["statement_id"].startswith(("st-chp7-p200-plate32a-", "st-chp7-p200-plate32b-"))]
        report = "s2-independent-review-chp5-20261022.md" if revision == "bfc87028" else "s2-independent-review-chp7-notes-20261021.md"
        add("H9622-" + revision, snap, selected, count, REPORT + report + "; scope=" + (segment or "Plate 32a-32b"))
        del snap
    snap = snapshot("2ef94174")
    add("H9617-chp7-p189-rereview", snap, [r for r in snap["rows"] if r["statement_id"].startswith("st-chp7-p189-")],
        44, REPORT + "s2-independent-review-chp7-p189-20261024.md; scope=initial 44-row rereview")
    del snap
    snap = snapshot("1a6313c8")
    five = {"st-chp7-p189-i25", "st-chp7-p189-i25-subject", "st-chp7-p189-i25-intended-gift", "st-chp7-p189-i26", "st-chp7-p189-i27"}
    add("H9622-chp7-p189-five-current", snap, [r for r in snap["rows"] if r["statement_id"] in five],
        5, REPORT + "s2-independent-review-chp7-p189-20261024.md; scope=2026-10-27 five current versions")
    del snap
    assert len(events) == 9622
    latest, event_counts = {}, Counter()
    for event in events:
        latest[event["statement_id"]] = event
        event_counts[event["statement_id"]] += 1
    assert len(latest) == 9539
    extra_fields = ["history_9622_event_count", "history_9622_latest_review_commit",
                    "history_9622_latest_statement_sha256", "history_9622_current_statement_match",
                    "history_9622_source_match", "history_9622_mention_delta", "history_9622_evidence_ref"]
    fields = list(roster[0]) + [k for k in extra_fields if k not in roster[0]]
    for row in roster:
        event = latest.get(row["statement_id"])
        row["history_9622_membership"] = "reconstructed_member" if event else "not_in_reconstructed_count"
        for key in extra_fields:
            row[key] = ""
        row["history_9622_event_count"] = str(event_counts[row["statement_id"]])
        if not event:
            continue
        row["history_9622_latest_review_commit"] = event["review_snapshot_commit"]
        row["history_9622_latest_statement_sha256"] = event["review_statement_sha256"]
        row["history_9622_current_statement_match"] = event["current_statement_match"]
        row["history_9622_source_match"] = event["current_source_match"]
        row["history_9622_mention_delta"] = event["mention_delta"]
        ref = RELATIVE_LEDGER + "#" + event["history_event_id"]
        row["history_9622_evidence_ref"] = ref
        row["prior_review_match"] = "exact_object_and_source_segment" if event["current_statement_match"] == "exact" and event["current_source_match"] == "true" else "historical_object_or_source_differs"
        if row["current_review_status"] != "reviewed_current_pass":
            row["current_review_status"] = "prior_review_mapped_open" if row["prior_review_match"] == "exact_object_and_source_segment" else "needs_delta_review"
            row["prior_review_ref"] = ref
            row["follow_up_note"] = "Historical direct reading is reusable for unchanged content; retain recorded open findings. Review only statement/source/mention deltas. Reconciliation does not grant semantic acceptance."
    ledger_data = csv_bytes(events, list(events[0]))
    roster_data = csv_bytes(roster, fields)
    summary = {
        "historical_counted_events": len(events), "historical_unique_ids": len(latest),
        "repeat_count_events": len(events) - len(latest),
        "latest_statement_match": dict(Counter(e["current_statement_match"] for e in latest.values())),
        "latest_source_match": dict(Counter(e["current_source_match"] for e in latest.values())),
        "absent_current_ids": sorted(sid for sid in latest if sid not in current_by_id),
        "current_ids_outside_count": len(set(current_by_id) - set(latest)),
        "roster_status_counts": dict(Counter(r["current_review_status"] for r in roster)),
        "batches": batches,
        "ledger_sha256": hashlib.sha256(ledger_data).hexdigest(),
        "roster_sha256": hashlib.sha256(roster_data).hexdigest(),
    }
    plan_hash = digest(summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("plan_sha256=" + plan_hash)
    if args.apply:
        if args.expect_plan != plan_hash:
            raise SystemExit("Apply requires --expect-plan matching the inspected dry-run")
        LEDGER.write_bytes(ledger_data)
        ROSTER.write_bytes(roster_data)
        print("applied_history_and_current_roster")


if __name__ == "__main__":
    main()
