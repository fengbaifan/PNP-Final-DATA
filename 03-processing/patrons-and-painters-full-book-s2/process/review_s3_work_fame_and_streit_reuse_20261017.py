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

REVIEWS = {
    "cand-6888": {
        "prior_group": "workgrp-0c379bfa64b197",
        "ku_id": "units/works/baldassare-franceschini-fame-carrying-the-name-of-louis-xiv-to-the-temple-of-immortality",
        "card_path": "04-knowledge/units/works/baldassare-franceschini-fame-carrying-the-name-of-louis-xiv-to-the-temple-of-immortality.md",
        "statement_ids": [
            "st-chp7-p187-i04",
            "st-chp20-plate66-franceschini-painting-attribution",
            "st-chp20-p403-alazard-commissioned-franceschini-picture",
        ],
        "source_checks": {
            "02-sources/02-Markdown/07_CHP-7_sec_i.md": [
                "In Florence Baldassare Franceschini was commissioned to paint Fame carrying the Name os the King to the Temple of Immortality."
            ],
            "02-sources/02-Markdown/20_CHP-20Postscript.md": [
                "Baldassare Franceschini: Fame carrying the name of Louis XIV to the Temple of Immortality",
                "Fame Carrying the Name os the King to the Temple of Immortality",
            ],
        },
        "card_checks": [
            "Fame carrying the name of Louis XIV to the Temple of Immortality",
            "图版编号 | 66",
            "Baldassare Franceschini",
        ],
        "rationale": (
            "第7章 p.187 的委托记述、第20章 Plate 66 图注及 p.402–403 跨页回指均落在同一件弗兰切斯基尼作品；Plate 66 已由既有 KU 收录。图注以 Louis XIV 具体化正文的 ‘the King’，是同一作品的题名信息，不据此拆成第二件作品。委托者仍未具名；本次不新增作者、委托或现藏关系。"
        ),
    },
    "cand-9636": {
        "prior_group": "workgrp-f2a47c2cb10ac4",
        "ku_id": "units/works/amigoni-sigismund-streit",
        "card_path": "04-knowledge/units/works/amigoni-sigismund-streit.md",
        "statement_ids": [
            "st-chp10-p315-amigoni-portrait-depicts-streit",
            "st-chp10-plate53b-amigoni-sigismund-streit-portrait",
            "st-chp10-p316-amigoni-painted-streit-portrait-and-ten-other-pictures",
            "st-chp10-p316-n03-amigoni-portrait-painted-1739-sitter-age-52",
        ],
        "source_checks": {
            "02-sources/02-Markdown/10_CHP-10_sec_ii.md": [
                "who gazes at us from Amigoni’s portrait",
                "Amigoni, who painted his portrait and ten other pictures for him between 1739 and 1746",
                "His portrait of Streit, which is published by Zimmermann, was painted when the sitter was aged 52—i.e. in 1739."
            ],
        },
        "card_checks": [
            "Portrait of Sigismund Streit",
            "Amigoni: Sigismund Streit",
            "Streit.1",
            "obj:863940",
        ],
        "rationale": (
            "第10章 p.315 正文与 Plate 53b 图注共同识别 Amigoni 所绘 Streit 肖像；p.316 正文及注3将 Amigoni 为 Streit 所绘肖像与1739年、坐像者52岁相连。既有 KU 的题注和柏林馆藏对象 obj:863940（Streit.1）对应这一单件肖像。p.316 关于四幅 Streit 肖像的句子没有逐幅指认，本裁决不把四幅作品并为一件，也不推断其余三幅身份。"
        ),
    },
}
ANCHOR = '<a id="s3-reuse-fame-and-streit-works-20261017"></a>'


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def csv_bytes(path: Path, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    import io

    original = path.read_bytes()
    newline = "\r\n" if b"\r\n" in original else "\n"
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore", lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    bom = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
    return bom + output.getvalue().encode("utf-8")


def text_bytes(path: Path, text: str) -> bytes:
    original = path.read_bytes()
    newline = "\r\n" if b"\r\n" in original else "\n"
    if newline == "\r\n":
        text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    bom = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
    return bom + text.encode("utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"{label}: expected one exact match, found {count}")
    return text.replace(old, new, 1)


def group_of(row: dict[str, str]) -> str:
    match = re.search(r"(?:^|[;；\s])group=([^;；\s]+)", row.get("resolution_note", ""))
    return match.group(1) if match else ""


def count_s3(alignment_rows: list[dict[str, str]], candidate_types: dict[str, str]) -> dict[str, object]:
    decisions = [r for r in alignment_rows if r.get("candidate_id") and not r.get("external_source")]
    same = [r for r in decisions if r.get("decision") == "same"]
    new = [r for r in decisions if r.get("decision") == "new"]
    groups: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in new:
        key = (candidate_types.get(row.get("candidate_id", ""), ""), group_of(row))
        if not all(key):
            raise ValueError(f"new row missing type/group: {row.get('candidate_id')}")
        groups.setdefault(key, []).append(row)
    registered = [members for members in groups.values() if len({r.get("ku_id", "") for r in members}) == 1 and members[0].get("ku_id")]
    pending = [members for members in groups.values() if {r.get("ku_id", "") for r in members} == {""}]
    if len(registered) + len(pending) != len(groups):
        raise ValueError("partial or split new identity group exists")
    by_type: dict[str, dict[str, int]] = {}
    for kind in set(candidate_types.values()):
        same_kind = [r for r in same if candidate_types.get(r.get("candidate_id", "")) == kind]
        new_kind = [r for r in new if candidate_types.get(r.get("candidate_id", "")) == kind]
        groups_kind = [(t, g, m) for (t, g), m in groups.items() if t == kind]
        by_type[kind] = {
            "same_candidates": len(same_kind),
            "same_kus": len({r.get("ku_id", "") for r in same_kind if r.get("ku_id")}),
            "new_candidates": len(new_kind),
            "new_groups": len(groups_kind),
            "registered_groups": sum(bool(m[0].get("ku_id")) for _, _, m in groups_kind),
            "registered_members": sum(len(m) for _, _, m in groups_kind if m[0].get("ku_id")),
            "pending_groups": sum(not m[0].get("ku_id") for _, _, m in groups_kind),
            "pending_members": sum(len(m) for _, _, m in groups_kind if not m[0].get("ku_id")),
        }
    external = [r for r in alignment_rows if r.get("external_source")]
    return {
        "candidate_rows": len(decisions),
        "alignment_rows": len(alignment_rows),
        "external_rows": len(external),
        "same_candidates": len(same),
        "same_kus": len({r.get("ku_id", "") for r in same if r.get("ku_id")}),
        "new_candidates": len(new),
        "new_groups": len(groups),
        "registered_groups": len(registered),
        "registered_members": sum(map(len, registered)),
        "pending_groups": len(pending),
        "pending_members": sum(map(len, pending)),
        "by_type": by_type,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Review two work candidates that duplicate accepted work KUs.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment_rows = read_csv(ALIGNMENT)
    _, candidate_rows = read_csv(CANDIDATES)
    _, manifest_rows = read_csv(MANIFEST)
    candidate_types = {r["candidate_id"]: r["suggested_type"] for r in candidate_rows}
    candidates = {r["candidate_id"]: r for r in candidate_rows}
    statements: dict[str, dict[str, object]] = {}
    with STATEMENTS.open(encoding="utf-8-sig") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                statements[row["statement_id"]] = row

    accepted_paths = {
        line[2:].strip()
        for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines()
        if line.startswith("- ")
    }
    for candidate_id, review in REVIEWS.items():
        candidate = candidates.get(candidate_id)
        if not candidate or candidate.get("suggested_type") != "work":
            raise ValueError(f"candidate type changed: {candidate_id}")
        rows = [r for r in alignment_rows if r.get("candidate_id") == candidate_id and not r.get("external_source")]
        if len(rows) != 1 or rows[0].get("decision") != "new" or rows[0].get("ku_id"):
            raise ValueError(f"candidate is not the expected pending new row: {candidate_id}")
        if group_of(rows[0]) != review["prior_group"]:
            raise ValueError(f"prior identity group changed: {candidate_id}")
        group_members = [r for r in alignment_rows if r.get("decision") == "new" and group_of(r) == review["prior_group"]]
        if [r.get("candidate_id") for r in group_members] != [candidate_id]:
            raise ValueError(f"prior group membership changed: {candidate_id}")

        manifest = [r for r in manifest_rows if r.get("ku_id") == review["ku_id"]]
        if len(manifest) != 1 or manifest[0].get("type") != "work" or manifest[0].get("card_path") != review["card_path"]:
            raise ValueError(f"existing same-type work KU not found: {candidate_id}")
        card_path = ROOT / review["card_path"]
        if not card_path.is_file() or review["card_path"] not in accepted_paths:
            raise ValueError(f"accepted target card is missing: {candidate_id}")
        card = card_path.read_text(encoding="utf-8-sig")
        if any(fragment not in card for fragment in review["card_checks"]):
            raise ValueError(f"target card no longer identifies the same work: {candidate_id}")
        if not any(
            r.get("decision") == "same" and r.get("ku_id") == review["ku_id"] and not r.get("external_source")
            for r in alignment_rows
        ):
            raise ValueError(f"existing same mapping to target KU is missing: {candidate_id}")
        for source, fragments in review["source_checks"].items():
            content = (ROOT / source).read_text(encoding="utf-8-sig")
            if any(fragment not in content for fragment in fragments):
                raise ValueError(f"source text mismatch: {source}")
        for statement_id in review["statement_ids"]:
            row = statements.get(statement_id)
            if not row:
                raise ValueError(f"missing S2 statement: {statement_id}")
            q = row.get("qualifiers") or {}
            if candidate_id not in (
                row.get("subject_candidate_id"),
                row.get("object_candidate_id"),
                *(q.get("mentioned_candidate_ids") or []),
            ):
                raise ValueError(f"S2 statement does not support candidate: {statement_id}")
            if statement_id == "st-chp10-plate53b-amigoni-sigismund-streit-portrait" and q.get("printed_caption") != "b. Amigoni: Sigismund Streit":
                raise ValueError("Plate 53b printed-caption check changed")

    before = count_s3(alignment_rows, candidate_types)
    if (before["candidate_rows"], before["alignment_rows"], before["external_rows"], before["same_candidates"], before["same_kus"], before["new_candidates"], before["new_groups"], before["registered_groups"], before["registered_members"], before["pending_groups"], before["pending_members"]) != (12407, 12645, 238, 1894, 1040, 4965, 4780, 729, 900, 4051, 4065):
        raise ValueError(f"unexpected S3 baseline: {before}")
    if before["by_type"]["work"] != {
        "same_candidates": 235, "same_kus": 218, "new_candidates": 496, "new_groups": 481,
        "registered_groups": 50, "registered_members": 56, "pending_groups": 431, "pending_members": 440,
    }:
        raise ValueError(f"unexpected work baseline: {before['by_type']['work']}")
    if ANCHOR in KNOWLEDGE.read_text(encoding="utf-8-sig"):
        raise ValueError("S3 review record already exists")

    for candidate_id, review in REVIEWS.items():
        row = next(r for r in alignment_rows if r.get("candidate_id") == candidate_id and not r.get("external_source"))
        row["decision"] = "same"
        row["ku_id"] = review["ku_id"]
        row["process_ref"] = "S3-S4-full-book-2026-10-17"
        row["resolution_note"] += (
            f"; S3跨章复核 2026-10-17：原 new 组 {review['prior_group']} 撤回，same → {review['ku_id']}。"
            f"{review['rationale']} 原 new 组号及理由保留为裁决历史。"
        )

    after = count_s3(alignment_rows, candidate_types)
    if (after["same_candidates"], after["same_kus"], after["new_candidates"], after["new_groups"], after["registered_groups"], after["registered_members"], after["pending_groups"], after["pending_members"]) != (1896, 1040, 4963, 4778, 729, 900, 4049, 4063):
        raise ValueError(f"unexpected S3 result: {after}")
    if after["by_type"]["work"] != {
        "same_candidates": 237, "same_kus": 218, "new_candidates": 494, "new_groups": 479,
        "registered_groups": 50, "registered_members": 56, "pending_groups": 429, "pending_members": 438,
    }:
        raise ValueError(f"unexpected work result: {after['by_type']['work']}")

    knowledge = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge = replace_once(knowledge,
        "| work | 2,397 | 235 | 481 / 496 | 5 | 29 | 1,632 | 50 / 56 | 431 / 440 |",
        "| work | 2,397 | 237 | 479 / 494 | 5 | 29 | 1,632 | 50 / 56 | 429 / 438 |", "process work row")
    knowledge = replace_once(knowledge,
        "| **合计** | **12,407** | **1,894** | **4,780 / 4,965** | **8** | **100** | **5,440** | **729 / 900** | **4,051 / 4,065** |",
        "| **合计** | **12,407** | **1,896** | **4,778 / 4,963** | **8** | **100** | **5,440** | **729 / 900** | **4,049 / 4,063** |", "process total row")
    knowledge = replace_once(knowledge,
        "same 的 1,894 条候选指向 1,040 个既有 KU；new 候选组成 4,780 个类型内身份组，共 4,965 条映射。",
        "same 的 1,896 条候选指向 1,040 个既有 KU；new 候选组成 4,778 个类型内身份组，共 4,963 条映射。", "process S3 decision summary")
    knowledge = replace_once(knowledge, "；235 条外部身份记录另行保留。", "；238 条外部身份记录另行保留。", "process external row count")
    process_lines = [
        "",
        ANCHOR,
        "",
        "### S3 work：弗兰切斯基尼《Fame》与 Amigoni 施特赖特肖像复用既有 KU（2026-10-17）",
        "",
    ]
    for candidate_id, review in REVIEWS.items():
        process_lines.extend([
            f"- `{candidate_id}` 原裁为单成员 `new` 组 `{review['prior_group']}`，本次依据跨章／图版／对象记录改为 `same`，指向既有 [{review['ku_id']} KU](../../../{review['card_path']}). {review['rationale']} 旧组与理由保留在 alignment `resolution_note` 中，不再进入 S4。",
        ])
    process_lines.extend([
        "- 两项均未新建 KU，也未改写卡片、enrichment 或 `relations.csv`；相应 S2 关系候选仍按既有状态交 S6。",
        "- 更新后 S3：same=1,896（指向1,040个既有KU）；new=4,963（4,778组）。work 类型 same=237、new=494/479组；S4 新组待登记4,049组／4,063条映射。KU=1,748，enrichment=10,782。",
    ])
    knowledge += "\n".join(process_lines) + "\n"

    result = RESULT.read_text(encoding="utf-8-sig")
    result = replace_once(result,
        "12,407 个候选决定行中，same=1,894（指向1,040个既有 KU）、new=4,965（4,780个身份组）、conflict=8、excluded=100、undecided=5,440。S4 已登记729组、映射900条成员候选；尚待登记4,051组、4,065条映射。",
        "12,407 个候选决定行中，same=1,896（指向1,040个既有 KU）、new=4,963（4,778个身份组）、conflict=8、excluded=100、undecided=5,440。S4 已登记729组、映射900条成员候选；尚待登记4,049组、4,063条映射。", "result current status")
    result = replace_once(result, "| same | 1,894 | 指向 1,040 个既有 KU |", "| same | 1,896 | 指向 1,040 个既有 KU |", "result same row")
    result = replace_once(result, "| new | 4,965 | 按 4,780 个当前身份组进入 S4；每组登记一个 KU |", "| new | 4,963 | 按 4,778 个当前身份组进入 S4；每组登记一个 KU |", "result new row")
    result = replace_once(result, "2026-10-17 strict-stage 表审计通过：KU=1,748；candidates=12,407；alignments=12,645、unlinked=0；enrichment=10,782；errors=[]、s2_missing=[]。当前待登记 S4 的 new 候选映射为4,065条", "2026-10-17 strict-stage 表审计通过：KU=1,748；candidates=12,407；alignments=12,645、unlinked=0；enrichment=10,782；errors=[]、s2_missing=[]。当前待登记 S4 的 new 候选映射为4,063条", "result current audit line")
    result += (
        "\n\n### S3 跨章复核：两项作品复用既有 KU（2026-10-17）\n\n"
        "`cand-6888` 由 `new` 改为 `same` → [弗兰切斯基尼《Fame》作品 KU](../units/works/baldassare-franceschini-fame-carrying-the-name-of-louis-xiv-to-the-temple-of-immortality.md)：第7章委托记述与第20章 Plate 66、p.402–403 回指同一件作品。`cand-9636` 由 `new` 改为 `same` → [Amigoni《施特赖特肖像》KU](../units/works/amigoni-sigismund-streit.md)：第10章 p.315 图文、Plate 53b 与 p.316 注3的1739年肖像信息对应现有单件作品；四幅肖像的具体指代仍未确定。两条旧 new 组号和理由保留在 alignment 中；未新建 KU、字段或正式关系。\n\n"
        "更新后 S3 same=1,896（1,040个既有 KU），new=4,963（4,778组）；待登记 S4 为4,049组／4,063条映射。work 类型 same=237、new=494（479组）；KU=1,748，enrichment=10,782。"
    )

    preview = {
        "mode": "apply" if args.apply else "dry-run",
        "candidates": {
            candidate_id: {"prior_decision": "new", "current_decision": "same", "prior_group": review["prior_group"], "target_ku": review["ku_id"]}
            for candidate_id, review in REVIEWS.items()
        },
        "new_kus": 0,
        "manifest_changes": 0,
        "enrichment_changes": 0,
        "relations_changes": 0,
        "counts_after": {key: after[key] for key in ("same_candidates", "same_kus", "new_candidates", "new_groups", "registered_groups", "registered_members", "pending_groups", "pending_members")},
        "work_after": after["by_type"]["work"],
        "external_alignment_rows": after["external_rows"],
    }
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    if not args.apply:
        return 0

    ALIGNMENT.write_bytes(csv_bytes(ALIGNMENT, alignment_fields, alignment_rows))
    KNOWLEDGE.write_bytes(text_bytes(KNOWLEDGE, knowledge))
    RESULT.write_bytes(text_bytes(RESULT, result))
    print("applied: two pending work groups now reuse their accepted work KUs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
