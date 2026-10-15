from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
CANDIDATES, MENTIONS, STATEMENTS = (TABLES / name for name in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl"))
SEGMENTS, COVERAGE = TABLES / "segments.jsonl", TABLES / "s2-coverage.csv"
SEGMENT_ID = "chp-1:01_CHP-1_sec_i:l26-33"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_i.md"
PARENT_ID = "st-chp1-l125-131-new-churches"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    CANDIDATES: "3a611b2fbc1b0b9a93c209c6afaadb58e6e5682e4d81d28ec98ba3c13b8d1192",
    MENTIONS: "f9ce556c80f6fa9053eed7cacc164e99dbca37041c34dda407b8fe13cabc6182",
    STATEMENTS: "585fcc78a9d6259562addbe0f5d24498f764ba1d05420d45e9fcf8c53afdcd40",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    COVERAGE: "1352b756f0f0310c00d21bfc3bfe194b5a347d291b699db78b5c85fa6e636a4d",
    SOURCE: "fb6198d0392e70a23a2d9ed05c0d432d4466de4ba75cc96762e3b4e45a204c40",
}
BACKUPS = {p: p.with_name(p.name + ".bak-s2-chp1-churches-atomic-claims-20261015") for p in (CANDIDATES, MENTIONS, STATEMENTS)}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_csv(data: bytes):
    r = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    return list(r.fieldnames or []), list(r)


def csv_row(headers, row):
    b = io.StringIO(newline="")
    csv.DictWriter(b, fieldnames=headers, lineterminator="\n", extrasaction="ignore").writerow(row)
    return b.getvalue().encode("utf-8")


def append_bytes(data: bytes, addition: bytes) -> bytes:
    return data + (b"" if data.endswith((b"\n", b"\r")) else b"\n") + addition


def build():
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit(f"HEAD changed: expected {EXPECTED_HEAD}, got {head}")
    for p, expected in EXPECTED_HASHES.items():
        if sha(p.read_bytes()) != expected:
            raise SystemExit(f"{p.relative_to(ROOT)} hash changed")
    cb, mb, sb = CANDIDATES.read_bytes(), MENTIONS.read_bytes(), STATEMENTS.read_bytes()
    ch, cr = parse_csv(cb)
    mh, mr = parse_csv(mb)
    if len(cr) != 12_248 or len(mr) != 26_436:
        raise SystemExit("unexpected table counts")
    cid_set, mid_set = {r["candidate_id"] for r in cr}, {r["mention_id"] for r in mr}
    new_cids = {"cand-12271", "cand-12272"}
    new_mids = {"m-chp1-seci-new-orders-group", "m-chp1-seci-new-temples-group"}
    new_sids = {"st-chp1-l125-131-noble-church-building", "st-chp1-l125-131-foreign-communities-temples"}
    if cid_set & new_cids or mid_set & new_mids:
        raise SystemExit("a new candidate or mention ID already exists")

    segments = {r["segment_id"]: r for r in (json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip())}
    seg = segments.get(SEGMENT_ID)
    if not seg or sha(SOURCE.read_bytes()) != seg.get("asset_sha256"):
        raise SystemExit("S0 source or segment metadata mismatch")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[int(seg["line_start"]) - 1:int(seg["line_end"])])
    if sha(text.encode("utf-8")) != seg.get("sha256"):
        raise SystemExit("S0 segment hash mismatch")
    coverage = next((r for r in csv.DictReader(COVERAGE.open(encoding="utf-8-sig", newline="")) if r["segment_id"] == SEGMENT_ID), None)
    if not coverage or coverage.get("disposition") != "reviewed" or coverage.get("migration_status") != "complete":
        raise SystemExit("S2 segment is not reviewed/complete")
    surfaces = [("New Orders", "m-chp1-seci-new-orders-group", "cand-12271"), ("magnificent new temples", "m-chp1-seci-new-temples-group", "cand-12272")]
    new_mentions = []
    for surface, mid, cid in surfaces:
        if text.count(surface) != 1:
            raise SystemExit(f"source phrase not unique: {surface}")
        start = text.index(surface)
        end = start + len(surface)
        if any(r["segment_id"] == SEGMENT_ID and start < int(r["end_char"]) and end > int(r["start_char"]) for r in mr):
            raise SystemExit(f"source span overlaps a current mention: {surface}")
        new_mentions.append({"mention_id": mid, "segment_id": SEGMENT_ID, "candidate_id": cid, "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": "Source-defined collective endpoint; named examples remain separately mapped and membership is not inferred beyond the text."})

    order_members = ["cand-3402", "cand-3403", "cand-3404", "cand-2980", "cand-3405"]
    community_members = ["cand-11824", "cand-3407"]
    required = set(order_members + community_members + ["cand-3406", "cand-11823", "cand-3126"])
    if not required <= cid_set:
        raise SystemExit(f"existing endpoint candidates missing: {sorted(required - cid_set)}")
    statement_lines = sb.splitlines(keepends=True)
    decoded = []
    parent_i = None
    parent = None
    for i, raw in enumerate(statement_lines):
        if raw.strip():
            obj = json.loads(raw)
            decoded.append(obj)
            if obj.get("statement_id") == PARENT_ID:
                parent_i, parent = i, obj
    if parent is None or parent.get("segment_id") != SEGMENT_ID or parent.get("subject_candidate_id") not in (None, "") or parent.get("object_candidate_id") not in (None, ""):
        raise SystemExit("source statement changed or is no longer open at both endpoints")
    q = parent.get("qualifiers", {})
    if q.get("relation_candidate") is not True or q.get("source_line_start") != 125:
        raise SystemExit("parent statement classification or source anchor changed")
    if not new_sids.isdisjoint({r["statement_id"] for r in decoded}):
        raise SystemExit("a split statement ID already exists")
    original_quote = parent["original_quote"]

    candidates = [
        {"candidate_id":"cand-12271","index_entry_id":"","canonical_name":"New religious orders named by Haskell as responding to the Reformation (source-defined group)","index_page_range":"","suggested_type":"","status":"open","index_source_file":"","sub_entry":"","detail":"Source-defined collective of the Oratorians, Jesuits, Theatines, Barnabites and Capuchins, which Haskell says arose to meet the Reformation threat. The member institutions are mapped separately; no exact foundation dates are supplied. Type remains unset because the taxonomy has no institution-group type.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{SEGMENT_ID}#L125"},
        {"candidate_id":"cand-12272","index_entry_id":"","canonical_name":"Magnificent new temples erected by foreign communities in Rome (source-defined group)","index_page_range":"","suggested_type":"","status":"open","index_source_file":"","sub_entry":"","detail":"Haskell refers to a plural group of magnificent new temples erected by foreign communities in Rome but names no individual temple or count. Type remains unset because the taxonomy has no place-group type.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{SEGMENT_ID}#L131"},
    ]

    orders = dict(parent)
    orders["subject_candidate_id"], orders["object_candidate_id"] = "cand-12271", "cand-3406"
    oq = dict(q)
    oq["claim"] = "Haskell says a source-defined group of new religious orders arose to meet the threat of the Reformation; he names the Oratorians, Jesuits, Theatines, Barnabites and Capuchins."
    oq["participant_candidate_ids"] = order_members
    oq["relation_candidate_note"] = "The source explicitly links the named new-orders group to the Reformation threat. The five listed institutions remain separate participants; this is not a claim about any particular foundation event or date."
    oq.pop("open_endpoint_reason", None)
    orders["qualifiers"] = oq

    noble = dict(parent)
    noble["statement_id"] = "st-chp1-l125-131-noble-church-building"
    nq = dict(q)
    nq["claim"] = "Haskell says a noble could build a complete new church to add to Rome's splendour and provide a burial place for the noble's family."
    nq["qualification"] = "A generalized possibility, not a named church foundation or documented commission."
    nq["relation_candidate_note"] = "This clause describes a generic church-building possibility. No individual noble, church, or family burial site is identified."
    nq["open_endpoint_reason"] = "The agent and church are generic role references, not individually identified entities; the passage supplies no named foundation event."
    noble["qualifiers"] = nq

    temples = dict(parent)
    temples["statement_id"] = "st-chp1-l125-131-foreign-communities-temples"
    temples["subject_candidate_id"], temples["object_candidate_id"] = "cand-11823", "cand-12272"
    tq = dict(q)
    tq["claim"] = "Haskell says the foreign communities in Rome, including Florentines, Lombards and others, competed to erect magnificent new temples."
    tq["participant_candidate_ids"] = community_members
    tq["relation_candidate_note"] = "The source-defined Roman foreign-communities group is linked to a source-defined group of new temples; Florentines and Lombards remain examples, while other members and individual temples are unspecified."
    tq.pop("open_endpoint_reason", None)
    temples["qualifiers"] = tq

    for newrow in candidates:
        cb = append_bytes(cb, csv_row(ch, newrow))
    for newrow in new_mentions:
        mb = append_bytes(mb, csv_row(mh, newrow))
    end = b"\r\n" if statement_lines[parent_i].endswith(b"\r\n") else b"\n"
    statement_lines[parent_i] = json.dumps(orders, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + end
    statement_lines[parent_i + 1:parent_i + 1] = [json.dumps(noble, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + end, json.dumps(temples, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + end]
    sb = b"".join(statement_lines)
    _, cr2 = parse_csv(cb)
    _, mr2 = parse_csv(mb)
    sr2 = [json.loads(line) for line in sb.splitlines() if line.strip()]
    if len(cr2) != 12_250 or len(mr2) != 26_438 or len(sr2) != 15_111:
        raise SystemExit("projected counts do not match")
    if len({r["candidate_id"] for r in cr2}) != len(cr2) or len({r["mention_id"] for r in mr2}) != len(mr2) or len({r["statement_id"] for r in sr2}) != len(sr2):
        raise SystemExit("duplicate projected IDs")
    return {CANDIDATES:cb, MENTIONS:mb, STATEMENTS:sb}


def apply_transaction(updates):
    if any(p.exists() for p in BACKUPS.values()):
        raise SystemExit("recovery backup already exists")
    for p, expected in EXPECTED_HASHES.items():
        if sha(p.read_bytes()) != expected:
            raise SystemExit(f"{p.relative_to(ROOT)} changed after preview")
    for source, backup in BACKUPS.items():
        shutil.copy2(source, backup)
    temps, replaced = {}, []
    try:
        for target, data in updates.items():
            with tempfile.NamedTemporaryFile("wb", dir=target.parent, delete=False) as stream:
                temp = Path(stream.name); stream.write(data); stream.flush(); os.fsync(stream.fileno())
            temps[target] = temp
        for target, temp in temps.items():
            os.replace(temp, target); replaced.append(target)
    except Exception:
        for target in reversed(replaced): shutil.copy2(BACKUPS[target], target)
        raise
    finally:
        for temp in temps.values():
            if temp.exists(): temp.unlink()


def main():
    parser = argparse.ArgumentParser(description="Split one compound first-chapter statement into its source-supported claims.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preview", action="store_true"); modes.add_argument("--apply", action="store_true")
    args = parser.parse_args(); updates = build()
    print("split claim: new orders -> Reformation; generic noble building remains open; foreign communities -> new temples")
    print("projected candidates=12250 mentions=26438 statements=15111")
    for p, data in updates.items(): print(f"{p.relative_to(ROOT)}: {sha(p.read_bytes())} -> {sha(data)}")
    if args.preview: print("preview only; no files or backups written"); return
    apply_transaction(updates)
    print("applied; recovery backups created for candidates, mentions and statements")


if __name__ == "__main__": main()
