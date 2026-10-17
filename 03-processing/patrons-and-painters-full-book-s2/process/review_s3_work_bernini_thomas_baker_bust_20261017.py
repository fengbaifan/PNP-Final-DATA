from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"

CANDIDATE_ID = "cand-4436"
PRIOR_GROUP = "workgrp-5b3c6d0ce899cf"
KU_ID = "units/works/bernini-thomas-baker-bust"
CARD_PATH = "04-knowledge/units/works/bernini-thomas-baker-bust.md"
STATEMENT_IDS = [
    "st-chp1-secii-l106-116-01b",
    "st-chp1-secii-notes-bernini-prices",
    "st-chp1-secii-notes-bernini-bust-vna",
    "st-chp2-secii-l62-69-nicholas-stone-baker-bust-account",
    "st-chp7-p179-i09",
]
SOURCE_QUOTES = {
    "02-sources/02-Markdown/01_CHP-1_sec_ii.md": [
        "At the height of his fame Bernini was once paid 6000 scudi for a single portrait bust",
        "By the Englishman Thomas Baker for his bust now in the Victoria and Albert Museum",
    ],
    "02-sources/02-Markdown/02_CHP-2_sec_ii.md": [
        "when the artist was carving the bust of Thomas Baker",
    ],
    "02-sources/02-Markdown/07_CHP-7_sec_i.md": [
        "Thomas Baker, who took Van Dyck’s portrait to Rome, just managed to get the master to -record his own fantastical features before the Pope",
    ],
}
ANCHOR = '<a id="s3-reuse-bernini-thomas-baker-bust-20261017"></a>'


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def csv_bytes(path: Path, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    import io

    old = path.read_bytes()
    newline = "\r\n" if b"\r\n" in old else "\n"
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore", lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b"") + output.getvalue().encode("utf-8")


def text_bytes(path: Path, text: str) -> bytes:
    old = path.read_bytes()
    newline = "\r\n" if b"\r\n" in old else "\n"
    if newline == "\r\n":
        text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    return (b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b"") + text.encode("utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"{label}: expected one exact match, found {count}")
    return text.replace(old, new, 1)


def group_of(row: dict[str, str]) -> str:
    match = re.search(r"(?:^|[;；\s])group=([^;；\s]+)", row.get("resolution_note", ""))
    return match.group(1) if match else ""


def count_s3(alignment_rows: list[dict[str, str]], candidate_types: dict[str, str]) -> dict[str, object]:
    decided = [row for row in alignment_rows if row.get("candidate_id") and not row.get("external_source")]
    same_rows = [row for row in decided if row.get("decision") == "same"]
    same_kus = {row.get("ku_id", "") for row in same_rows if row.get("ku_id")}
    new_rows = [row for row in decided if row.get("decision") == "new"]
    groups: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in new_rows:
        key = (candidate_types.get(row.get("candidate_id", ""), ""), group_of(row))
        if not key[0] or not key[1]:
            raise ValueError(f"new row missing type/group: {row.get('candidate_id')}")
        groups.setdefault(key, []).append(row)
    registered = [members for members in groups.values() if len({x.get("ku_id", "") for x in members}) == 1 and members[0].get("ku_id")]
    pending = [members for members in groups.values() if {x.get("ku_id", "") for x in members} == {""}]
    if len(registered) + len(pending) != len(groups):
        raise ValueError("partial or split new identity group exists")
    by_type: dict[str, dict[str, int]] = {}
    for kind in set(candidate_types.values()):
        sr = [row for row in same_rows if candidate_types.get(row.get("candidate_id", "")) == kind]
        nr = [row for row in new_rows if candidate_types.get(row.get("candidate_id", "")) == kind]
        gr = [(t, g, m) for (t, g), m in groups.items() if t == kind]
        by_type[kind] = {
            "same_candidates": len(sr),
            "same_kus": len({row.get("ku_id", "") for row in sr if row.get("ku_id")}),
            "new_candidates": len(nr),
            "new_groups": len(gr),
            "registered_groups": sum(bool(members[0].get("ku_id")) for _, _, members in gr),
            "registered_members": sum(len(members) for _, _, members in gr if members[0].get("ku_id")),
            "pending_groups": sum(not members[0].get("ku_id") for _, _, members in gr),
            "pending_members": sum(len(members) for _, _, members in gr if not members[0].get("ku_id")),
        }
    return {
        "same_candidates": len(same_rows),
        "same_kus": len(same_kus),
        "new_candidates": len(new_rows),
        "new_groups": len(groups),
        "registered_groups": len(registered),
        "registered_members": sum(map(len, registered)),
        "pending_groups": len(pending),
        "pending_members": sum(map(len, pending)),
        "by_type": by_type,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile cand-4436 with the already accepted Bernini Thomas Baker bust KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment_rows = read_csv(ALIGNMENT)
    _, candidate_rows = read_csv(CANDIDATES)
    _, manifest_rows = read_csv(MANIFEST)
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    candidate_types = {row["candidate_id"]: row["suggested_type"] for row in candidate_rows}
    target_rows = [row for row in alignment_rows if row.get("candidate_id") == CANDIDATE_ID and not row.get("external_source")]
    if len(target_rows) != 1 or target_rows[0].get("decision") != "new" or target_rows[0].get("ku_id"):
        raise ValueError("candidate is not the expected single pending S3 new row")
    target = target_rows[0]
    if candidates.get(CANDIDATE_ID, {}).get("suggested_type") != "work" or group_of(target) != PRIOR_GROUP:
        raise ValueError("candidate type or prior group changed")
    group_rows = [row for row in alignment_rows if row.get("decision") == "new" and not row.get("external_source") and group_of(row) == PRIOR_GROUP]
    if [row.get("candidate_id") for row in group_rows] != [CANDIDATE_ID]:
        raise ValueError("prior S3 group membership changed")

    target_manifest = [row for row in manifest_rows if row.get("ku_id") == KU_ID]
    if len(target_manifest) != 1 or target_manifest[0].get("type") != "work" or target_manifest[0].get("card_path") != CARD_PATH:
        raise ValueError("existing same-type work KU not found")
    if not (ROOT / CARD_PATH).is_file():
        raise ValueError("accepted target card is missing")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    if CARD_PATH not in {line[2:].strip() for line in accepted.splitlines() if line.startswith("- ")}:
        raise ValueError("existing work KU is not in accepted.yml")
    if not any(row.get("candidate_id") == "cand-3182" and row.get("decision") == "same" and row.get("ku_id") == KU_ID and not row.get("external_source") for row in alignment_rows):
        raise ValueError("existing S3 same mapping to the target KU is missing")

    for source, quotes in SOURCE_QUOTES.items():
        content = (ROOT / source).read_text(encoding="utf-8-sig")
        if any(quote not in content for quote in quotes):
            raise ValueError(f"source text mismatch: {source}")
    with STATEMENTS.open(encoding="utf-8-sig") as handle:
        statements = {row["statement_id"]: row for row in (json.loads(line) for line in handle if line.strip())}
    for sid in STATEMENT_IDS:
        row = statements.get(sid)
        q = (row or {}).get("qualifiers") or {}
        if not row or q.get("relation_candidate") is not True:
            raise ValueError(f"cross-chapter S2 evidence changed: {sid}")
        if CANDIDATE_ID not in (row.get("subject_candidate_id"), row.get("object_candidate_id"), *(q.get("mentioned_candidate_ids") or [])):
            raise ValueError(f"S2 statement no longer supports candidate {CANDIDATE_ID}: {sid}")

    before = count_s3(alignment_rows, candidate_types)
    if (len(manifest_rows), len(alignment_rows), len(candidate_rows)) != (1748, 12645, 12407):
        raise ValueError("unexpected table baseline")
    if (before["same_candidates"], before["same_kus"], before["new_candidates"], before["new_groups"], before["pending_groups"], before["pending_members"]) != (1893, 1040, 4966, 4781, 4052, 4066):
        raise ValueError(f"unexpected S3 baseline: {before}")
    if before["by_type"]["work"] != {
        "same_candidates": 234, "same_kus": 218, "new_candidates": 497, "new_groups": 482,
        "registered_groups": 50, "registered_members": 56, "pending_groups": 432, "pending_members": 441,
    }:
        raise ValueError(f"unexpected work baseline: {before['by_type']['work']}")
    if ANCHOR in KNOWLEDGE.read_text(encoding="utf-8-sig"):
        raise ValueError("process review already exists")

    target["decision"] = "same"
    target["ku_id"] = KU_ID
    target["process_ref"] = "S3-S4-full-book-2026-10-17"
    target["resolution_note"] += (
        "; S3 cross-chapter review 2026-10-17: prior new group superseded; same as " + KU_ID +
        ". Chapter 1 p.17 (st-chp1-secii-l106-116-01b; st-chp1-secii-notes-bernini-prices; st-chp1-secii-notes-bernini-bust-vna) identifies the 6,000-scudi portrait bust with Thomas Baker and reports its then-location at the V&A. Chapter 2 p.37 (st-chp2-secii-l62-69-nicholas-stone-baker-bust-account) reports Bernini carving Baker's bust while Baker carried Van Dyck's triple portrait of Charles I; Chapter 7 p.179 (st-chp7-p179-i09) says Baker got Bernini to record his own features. These references identify the existing Bernini bust of Thomas Baker; the Van Dyck portrait of Charles I is a separate work. Baker's precise transaction role remains source-limited. Prior new group " + PRIOR_GROUP + " retained as history."
    )
    after = count_s3(alignment_rows, candidate_types)
    if (after["same_candidates"], after["same_kus"], after["new_candidates"], after["new_groups"], after["registered_groups"], after["registered_members"], after["pending_groups"], after["pending_members"]) != (1894, 1040, 4965, 4780, 729, 900, 4051, 4065):
        raise ValueError(f"unexpected S3 result: {after}")
    if after["by_type"]["work"] != {
        "same_candidates": 235, "same_kus": 218, "new_candidates": 496, "new_groups": 481,
        "registered_groups": 50, "registered_members": 56, "pending_groups": 431, "pending_members": 440,
    }:
        raise ValueError(f"unexpected work result: {after['by_type']['work']}")

    knowledge = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge = replace_once(knowledge,
        "| work | 2,397 | 234 | 482 / 497 | 5 | 29 | 1,632 | 50 / 56 | 432 / 441 |",
        "| work | 2,397 | 235 | 481 / 496 | 5 | 29 | 1,632 | 50 / 56 | 431 / 440 |", "process work row")
    knowledge = replace_once(knowledge,
        "| **合计** | **12,407** | **1,893** | **4,781 / 4,966** | **8** | **100** | **5,440** | **729 / 900** | **4,052 / 4,066** |",
        "| **合计** | **12,407** | **1,894** | **4,780 / 4,965** | **8** | **100** | **5,440** | **729 / 900** | **4,051 / 4,065** |", "process total row")
    knowledge = replace_once(knowledge,
        "same 的 1,893 条候选指向 1,040 个既有 KU；new 候选组成 4,781 个类型内身份组，共 4,966 条映射。",
        "same 的 1,894 条候选指向 1,040 个既有 KU；new 候选组成 4,780 个类型内身份组，共 4,965 条映射。", "process S3 decision summary")
    knowledge += "\n".join([
        "", ANCHOR, "", "### S3 复核：Thomas Baker 胸像跨章复用既有 KU（2026-10-17）", "",
        "- `cand-4436` 原裁为单成员 `new` 组 `workgrp-5b3c6d0ce899cf`，现经跨章比对改为 `same`，映射至既有[贝尔尼尼的托马斯·贝克肖像胸像](../../../04-knowledge/units/works/bernini-thomas-baker-bust.md)。既有 same 候选 `cand-3182` 已指向该 KU。原 `new` 决定及组号留在 alignment 注释中作历史，不再作为待登记组。",
        "- 第1章 p.17 将一件 6,000 scudi 的肖像胸像与 Thomas Baker 联系，并记 Haskell 当时所称 V&A 收藏（S2：`st-chp1-secii-l106-116-01b`、`st-chp1-secii-notes-bernini-prices`、`st-chp1-secii-notes-bernini-bust-vna`）。第2章 p.37 据 Nicholas Stone 的记述称 Bernini 正在雕刻 Baker 胸像，同时说明 Baker 受托把 Van Dyck 的 Charles I 三人肖像带给 Bernini（`st-chp2-secii-l62-69-nicholas-stone-baker-bust-account`）。第7章 p.179 又述 Baker 让 Bernini记录自己的面貌（`st-chp7-p179-i09`）。合并指向同一胸像；Charles I 肖像保持为另一件作品。",
        "- 该身份判断不消除 Baker 在第1章压缩脚注中的角色歧义，也不新增或改写正式关系。现有 `rel-0452`–`rel-0454` 与其他 S2 候选交 S6 对照；本次未改 `relations.csv`、KU 卡片或 enrichment。",
        "- 更新后 S3：same=1,894（指向1,040个既有KU）；new=4,965（4,780组）。work 类型 same=235、new=496/481组；S4 新组待登记4,051组／4,065条映射。KU=1,748，enrichment=10,782。",
    ]) + "\n"

    result = RESULT.read_text(encoding="utf-8-sig")
    result = replace_once(result,
        "12,407 个候选决定行中，same=1,893（指向1,040个既有 KU）、new=4,966（4,781个身份组）、conflict=8、excluded=100、undecided=5,440。S4 已登记729组、映射900条成员候选；尚待登记4,052组、4,066条映射。",
        "12,407 个候选决定行中，same=1,894（指向1,040个既有 KU）、new=4,965（4,780个身份组）、conflict=8、excluded=100、undecided=5,440。S4 已登记729组、映射900条成员候选；尚待登记4,051组、4,065条映射。", "result current status")
    result = replace_once(result, "| same | 1,893 | 指向 1,040 个既有 KU |", "| same | 1,894 | 指向 1,040 个既有 KU |", "result same row")
    result = replace_once(result, "| new | 4,966 | 按 4,781 个当前身份组进入 S4；每组登记一个 KU |", "| new | 4,965 | 按 4,780 个当前身份组进入 S4；每组登记一个 KU |", "result new row")
    result = replace_once(result, "| work | 234→218 | 497／482 | 50／432；441 | 5 | 29 | 1,632 |", "| work | 235→218 | 496／481 | 50／431；440 | 5 | 29 | 1,632 |", "result work row")
    result = replace_once(result, "| **合计** | **1,893→1,040** | **4,966／4,781** | **729／4,052；4,066** | **8** | **100** | **5,440** |", "| **合计** | **1,894→1,040** | **4,965／4,780** | **729／4,051；4,065** | **8** | **100** | **5,440** |", "result S3/S4 total row")
    result = replace_once(result,
        "2026-10-17 strict-stage 表审计通过：KU=1,748；candidates=12,407；alignments=12,645、unlinked=0；enrichment=10,782；errors=[]、s2_missing=[]。当前待登记 S4 的 new 候选映射为4,066条",
        "2026-10-17 strict-stage 表审计通过：KU=1,748；candidates=12,407；alignments=12,645、unlinked=0；enrichment=10,782；errors=[]、s2_missing=[]。当前待登记 S4 的 new 候选映射为4,065条", "result strict audit")
    result += (
        "\n\n### S3 复核：Thomas Baker 胸像跨章复用既有 KU（2026-10-17）\n\n"
        "`cand-4436` 从 pending `new` 组改为 `same`，映射至既有[Bernini 的 Thomas Baker 胸像 KU](../units/works/bernini-thomas-baker-bust.md)。第1章价格与注释、第2章 Nicholas Stone 记述和第7章 Baker 本人像描述共同支持同一胸像；Van Dyck 的 Charles I 三人肖像保持区分。Baker 的精确交易角色仍按原文保留待证；既有正式边与新 S2 关系候选不在本次改动。"
        "S3 当前 same=1,894（1,040个既有 KU），new=4,965（4,780组）；待登记 S4 为4,051组／4,065条映射。KU=1,748，enrichment=10,782。"
    )

    preview = {
        "mode": "apply" if args.apply else "dry-run",
        "candidate_id": CANDIDATE_ID,
        "prior_decision": "new",
        "current_decision": "same",
        "target_ku": KU_ID,
        "prior_group_retained_as_history": PRIOR_GROUP,
        "cross_chapter_statements": STATEMENT_IDS,
        "new_ku_count": 0,
        "manifest_changes": 0,
        "enrichment_changes": 0,
        "relations_changes": 0,
        "counts_after": {k: after[k] for k in ("same_candidates", "same_kus", "new_candidates", "new_groups", "registered_groups", "registered_members", "pending_groups", "pending_members")},
        "work_after": after["by_type"]["work"],
    }
    print(json.dumps(preview, ensure_ascii=True, indent=2))
    if not args.apply:
        return 0

    ALIGNMENT.write_bytes(csv_bytes(ALIGNMENT, alignment_fields, alignment_rows))
    KNOWLEDGE.write_bytes(text_bytes(KNOWLEDGE, knowledge))
    RESULT.write_bytes(text_bytes(RESULT, result))
    print("applied: cand-4436 now reuses the existing Thomas Baker bust KU; no new KU, enrichment, or relation added")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
