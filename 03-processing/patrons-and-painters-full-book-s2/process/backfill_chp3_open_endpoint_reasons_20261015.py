from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/stages.md"
EXPECTED_TABLE_SHA256 = "41df39d32ca0a80aeb65146fab0a78e89d24b8fda5feb7ae70cd13ec06f1a6bc"
SOURCE_ASSET_SHA256 = "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed"
SEGMENT_HASHES = {
    "chp-3:03_CHP-3_sec_iv:l16-24": "2860061ec609cd932cec37cf53cdc868bf293fb348c3431fd86d26f976c4ddbe",
    "chp-3:03_CHP-3_sec_iv:l165-177": "31d51a622ebe4435aba123bb7584365b46a72264ce8b84261771e0033a17f19e",
    "chp-3:03_CHP-3_sec_iv:l189-243": "a1c4488eadee5a37875ea5ba4e8afa1bbc77001b5fd6ad6682b91106e7f1c329",
}
REASONS = {
    "st-chp3-seciv-l16-24-oliva-took-advantage-of-new-situation": (
        "Haskell explicitly presents Oliva's taking advantage of the 'new situation' as an inference, but does not identify a separate bounded situation or event. Preserve the author's inference and leave its referent unresolved; do not infer it from adjacent events."
    ),
    "st-chp3-seciv-l165-177-special-references-to-cardinal-savelli": (
        "The source says the patronage concession was exchanged for special references to Cardinal Savelli's ancestor, but does not identify who would make the references or where they would appear. Keep the agent endpoint open."
    ),
    "st-chp3-seciv-l165-177-letters-carried-complaints-to-duke": (
        "The narrative says signed and anonymous letters reached the father in charge, then separately says the Duke was told the allegations. It does not identify the informant or establish that the letters were the source of the report to the Duke."
    ),
    "st-chp3-seciv-l165-177-more-architects-consulted": (
        "The passive statement says more architects were consulted but does not name who consulted them. Preserve the source-defined architect group and leave the consulting agent unresolved."
    ),
    "st-chp3-seciv-l165-177-pozzo-given-charge-of-altar": (
        "The source says Pozzo was put in complete charge but does not name the appointing agent. Although Tirso Gonzalez's decision is described immediately before, the text does not explicitly attribute the appointment to him; do not infer the agent."
    ),
    "st-chp3-seciv-notes-l189-204-p79-n2-joshua-subject-compared-with-carlone": (
        "Note 2 says the subject matches the one chosen for Carlone's project at the Jesuit church in Perugia but does not identify that subject. Carlone is the painter, not the comparison target; the cited study is not independently available in this record."
    ),
    "st-chp3-seciv-notes-l205-243-p93-n1-proposal-to-move-legros-figure": (
        "The note reports a proposal to move Legros's figure to 'the church itself' but does not name the destination church. The cited study is not independently available in this record, so retain the destination as open."
    ),
}
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp3-open-reasons-20261015")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_open(row: dict) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def open_counts(rows: list[dict]) -> tuple[int, int, int, int]:
    opened = [row for row in rows if is_open(row)]
    obj_only = sum(bool(row.get("subject_candidate_id")) and not row.get("object_candidate_id") for row in opened)
    subj_only = sum(not row.get("subject_candidate_id") and bool(row.get("object_candidate_id")) for row in opened)
    both = sum(not row.get("subject_candidate_id") and not row.get("object_candidate_id") for row in opened)
    return len(opened), obj_only, subj_only, both


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    if digest(raw) != EXPECTED_TABLE_SHA256:
        raise ValueError(f"statement table changed: {digest(raw)}")
    if digest(SOURCE.read_bytes()) != SOURCE_ASSET_SHA256:
        raise ValueError("chapter 3 source asset changed")
    segments = {
        row["segment_id"]: row
        for row in (json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip())
    }
    for segment_id, expected_hash in SEGMENT_HASHES.items():
        row = segments.get(segment_id)
        if not row or row.get("sha256") != expected_hash or row.get("asset_sha256") != SOURCE_ASSET_SHA256:
            raise ValueError(f"reviewed source segment changed: {segment_id}")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    for evidence in (
        "Oliva“利用新局面”仍指向未界定情境",
        "来信与告知公爵的来源是否相同、Pozzo任命者、Savelli纪念性致辞的执行方、咨询建筑师的主体，原文均不足以确定",
        "Carlone同题材身份及“the church itself”目的地也继续开放，需取得注文所引研究全文后再判断",
    ):
        if evidence not in process_text:
            raise ValueError(f"required S2 decision not found in process log: {evidence}")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError("duplicate statement IDs in input")
    if open_counts(rows) != (390, 244, 46, 100):
        raise ValueError(f"unexpected open-endpoint state: {open_counts(rows)}")
    for statement_id in REASONS:
        row = by_id.get(statement_id)
        if not row or not is_open(row) or (row.get("qualifiers") or {}).get("open_endpoint_reason"):
            raise ValueError(f"expected unresolved, reasonless statement changed: {statement_id}")

    for statement_id, reason in REASONS.items():
        by_id[statement_id]["qualifiers"]["open_endpoint_reason"] = reason
    output = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows).encode("utf-8")
    after_counts = open_counts(rows)
    if after_counts != (390, 244, 46, 100):
        raise ValueError(f"open endpoint count changed unexpectedly: {after_counts}")

    print("reviewed=seven chapter 3 open endpoints, reconciled against the existing S2 process decision")
    print("result=added row-level reasons; no endpoint or relation classification changed")
    print("no_reason_open=82->75; open_endpoints=390,244,46,100 (unchanged)")
    print(f"book-statements.jsonl sha256 {digest(raw)}->{digest(output)}")
    if args.preview:
        return 0
    if BACKUP.exists():
        raise FileExistsError(f"recovery copy already exists: {BACKUP.name}")
    temp = TABLE.with_name("book-statements.jsonl.tmp-s2-chp3-open-reasons-20261015")
    if temp.exists():
        raise FileExistsError(f"temporary file already exists: {temp.name}")
    shutil.copy2(TABLE, BACKUP)
    try:
        temp.write_bytes(output)
        temp.replace(TABLE)
    except Exception:
        if temp.exists():
            temp.unlink()
        shutil.copy2(BACKUP, TABLE)
        raise
    print(f"backup={BACKUP.relative_to(ROOT)}")
    print(f"applied_sha256={digest(TABLE.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
