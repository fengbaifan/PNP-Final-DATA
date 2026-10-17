from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

GROUP = "new-person:cozza-francesco-f2b1f96cec"
MEMBERS = ("cand-0867",)
KU_ID = "units/persons/francesco-cozza"
CARD_PATH = "04-knowledge/units/persons/francesco-cozza.md"
DATE = "2026-10-17"
PROCESS_ANCHOR = "s3-s4-person-francesco-cozza-20261017"
TRECCANI_URL = "https://www.treccani.it/enciclopedia/francesco-cozza_(Dizionario-Biografico)/"
DIRECT_RELATIONS = (
    "st-chp5-p131-cozza-altarpiece",
    "st-chp5-p131-cozza-probably-recommended",
    "st-chp5-p131-shared-pupilage",
    "st-chp5-p131-almost-certain-association",
)

QUOTE = (
    "As the same priests also employed their fellow-Calabrian Francesco Cozza on an altar painting "
    "it was probably he who recommended Sassoferrato, for both had been pupils of Domenichino "
    "and were almost certainly associated."
)

RECORD = {
    "name_zh": "弗朗切斯科·科扎",
    "name_en": "Francesco Cozza",
    "description_zh": (
        "哈斯克尔在第5章 p.131 以全名 Francesco Cozza 指称一名卡拉布里亚人，并记述同一批祭司也雇用他绘制一幅祭坛画。"
        "同段将 Cozza 置于与 Sassoferrato 的推荐、共同师承及交往叙述中；“probably”与“almost certainly”保留为原作者限定，"
        "四条关系候选均待 S6 逐项审查。Treccani《意大利人传记辞典》条目用于核对人物身份，不据此补入生卒、地点或作品事实。"
    ),
    "description_en": (
        "On p. 131 of chapter 5, Haskell names Francesco Cozza, calls him a fellow-Calabrian, and says the same priests also employed him "
        "on an altar painting. The passage places Cozza in claims about recommending Sassoferrato, their shared pupilage, and their association; "
        "the author's qualifiers “probably” and “almost certainly” are retained, and all four relation candidates remain for individual S6 review. "
        "The Treccani Dizionario Biografico degli Italiani entry is used to compare identity only; no dates, places, or works are imported from it."
    ),
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note: str):
    match = re.search(r"group=([^;| ]+)", note)
    return match.group(1) if match else None


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"expected one {label} anchor; found {count}")
    return text.replace(old, new, 1)


def make_card():
    source = card_writer.source(
        "5", "131", "05_CHP-5_sec_i.md", "119", QUOTE,
        "哈斯克尔称同一批祭司也雇用卡拉布里亚人 Francesco Cozza 绘制祭坛画；他可能推荐了 Sassoferrato，两人都曾师从 Domenichino，且几乎可以肯定有交往。各处限定按原文保留。",
    )
    book_source = {
        "citation": card_writer.BOOK_CITATION,
        "location": "第5章，印刷页131；OCR L119",
        "sentence_summary": source["summary"],
        "original_quotes": [{"source_span": "lines 119", "text": QUOTE}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
            "source_span": "lines 119; print p. 131",
        },
    }
    frontmatter = {
        "title": f"{RECORD['name_zh']}（{RECORD['name_en']}）",
        "name_en": RECORD["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [book_source],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = card_writer.yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** {RECORD['description_zh']}

**English:** {RECORD['description_en']}

### 名称

中文显示名及英文显示名见卡片标题；中文名为便于识别所用音译，原书拼写按来源引文保留。

The bilingual display names appear in the card title. The Chinese name is a transliteration for readability; the source spelling is preserved in the quotation.

### 身份核对

Treccani《意大利人传记辞典》（Ludovica Trezzani，vol. 30，1984）[“COZZA, Francesco”条目]({TRECCANI_URL})，访问于 {DATE}。该条目以全名收录一位卡拉布里亚画家并记其师从 Domenichino；全名、地域与师承语境与本书第5章 p.131 相合。此处仅记录身份比对，不把外部条目的生平或作品资料作为本卡新增事实，也不据此将原书的推荐或交往表述升格为关系事实。

### 身份边界

中文：本书这一处将 Francesco Cozza 作为人物称名；未据姓名相似另合并其他 KU。这里的西班牙语术语、未具名祭司群体和未识别祭坛画均不是 Cozza 的人物身份替代物。

English: This passage names Francesco Cozza as a person; no other KU is merged on name similarity alone. The unnamed priest group and unidentified altar painting are separate unresolved objects, not alternate identities for Cozza.

## 关系与证据

本卡未新增正式关系。以下四条 S2 关系候选保留原文语气并待 S6：`st-chp5-p131-cozza-altarpiece`（祭司雇用 Cozza 绘制未识别祭坛画；`cand-6068` 群体未分类，`cand-6069` 作品仍待消歧）；`st-chp5-p131-cozza-probably-recommended`（原作者称“probably”由 Cozza 推荐 Sassoferrato）；`st-chp5-p131-shared-pupilage`（原文称 Cozza 与 Sassoferrato 均师从 Domenichino）；`st-chp5-p131-almost-certain-association`（原作者称两人“almost certainly associated”；Sassoferrato 身份候选 `cand-2369` 仍为 `undecided`）。身份核对不替代关系裁决。
"""
    return f"---\n{fm}---\n\n{body}"


def s3_resolution(old_note: str) -> str:
    return (
        f"source_ref=candidate=cand-0867;index_entry=C.csv#400;index_pages=131; group={GROUP}; "
        "S3 identity review 2026-10-17: retain new as one source-local person. The index full-name form ‘Cozza, Francesco’ and ch.5 p.131 full-name mention ‘Francesco Cozza’ identify one person; the local person manifest has no matching Cozza KU. "
        "Treccani DBI, Ludovica Trezzani, vol. 30 (1984), entry ‘COZZA, Francesco’ (https://www.treccani.it/enciclopedia/francesco-cozza_(Dizionario-Biografico)/; accessed 2026-10-17) identifies a Calabrian painter and notes his pupilage with Domenichino; name, regional context, and training context match Haskell’s p.131. This corroborates identity only; it does not establish Haskell’s qualified recommendation or association claims. "
        "prior_resolution_note=" + old_note
    )


def update_process(text: str, registered_groups: int, registered_members: int, pending_groups: int, pending_members: int, manifest_count: int) -> str:
    if f'<a id="{PROCESS_ANCHOR}"></a>' in text:
        return text
    entry = f"""

<a id="{PROCESS_ANCHOR}"></a>

### S3→S4 person：Francesco Cozza 单人身份组核对与登记（{DATE}）

`cand-0867`（C.csv#400，索引页131）保留 `new`，登记为 `{GROUP}`／`{KU_ID}`。索引全名“Cozza, Francesco”与第5章 p.131 正文全名“Francesco Cozza”相合；人物 manifest 中没有同名 KU。外部身份比对使用 Ludovica Trezzani，*Dizionario Biografico degli Italiani*，vol. 30（1984），Treccani 条目[“COZZA, Francesco”]({TRECCANI_URL})（访问：{DATE}）：条目以全名收录一位卡拉布里亚画家，并记其师从 Domenichino，与 Haskell p.131 的姓名、同乡和师承语境相合。此来源仅作身份佐证，不将生平或作品事实导入卡片；不裁决原文的推荐、师承或交往关系。

S4 新建[Francesco Cozza 人物卡](../../../04-knowledge/units/persons/francesco-cozza.md)，并把候选 `aln-1202` 映射到 `{KU_ID}`；外部身份比对作为独立 alignment 行保存。4条直接 S2 关系候选 `st-chp5-p131-cozza-altarpiece`、`st-chp5-p131-cozza-probably-recommended`、`st-chp5-p131-shared-pupilage`、`st-chp5-p131-almost-certain-association` 均未正式化，待 S6。相关端点状态分别为：未具名祭司群体 `cand-6068` 仍 `undecided`／未分类；祭坛画 `cand-6069` 仍 `undecided`／作品身份未识别；Sassoferrato `cand-2369` 仍 `undecided`；Domenichino `cand-0932` 已复用既有 KU。不得将 Treccani 身份佐证作为上述关系成立的证据。

S4 当前登记 {registered_groups} 组／{registered_members} 条候选映射；待登记 {pending_groups} 组／{pending_members} 条映射；KU 总数 {manifest_count}。
"""
    return text.rstrip() + entry


def update_result(text: str, registered_groups: int, registered_members: int, pending_groups: int, pending_members: int, manifest_count: int, alignment_count: int, external_count: int, pending_new_count: int) -> str:
    text = replace_once(
        text,
        "S4 已登记522组、映射652条成员候选；尚待登记4,282组、4,326条映射。",
        f"S4 已登记{registered_groups:,}组、映射{registered_members:,}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。",
        "current S4 top-line count",
    )
    text = replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,541 KU", f"| [KU 登记](../tables/ku-manifest.csv) | {manifest_count:,} KU", "manifest count")
    text = replace_once(
        text,
        "| [全书对齐](../tables/alignment.csv) | 12,635 条：12,407 条候选决定记录及 228 条外部身份记录；候选决定数见下表 |",
        f"| [全书对齐](../tables/alignment.csv) | {alignment_count:,} 条：12,407 条候选决定记录及 {external_count:,} 条外部身份记录；候选决定数见下表 |",
        "alignment row count",
    )
    old_audit = re.compile(r"审计警告中的[\d,]+条待登记 `decision=new` alignment 行，含[\d,]+条候选决定映射（[\d,]+组）和[\d,]+条外部身份记录。")
    replacement = (
        f"审计警告中的{pending_new_count:,}条待登记 `decision=new` alignment 行，含{pending_members:,}条候选决定映射（{pending_groups:,}组）和15条外部身份记录。"
    )
    text, substitutions = old_audit.subn(replacement, text)
    if substitutions != 1:
        raise AssertionError(f"expected one audit-warning count; found {substitutions}")
    text = replace_once(
        text,
        "S4当前登记522组/652条候选映射；待登记4,282组/4,326条；KU总数1,541。",
        f"S4当前登记{registered_groups:,}组/{registered_members:,}条候选映射；待登记{pending_groups:,}组/{pending_members:,}条；KU总数{manifest_count:,}。",
        "current S4 end-of-result count",
    )
    heading = "### S3→S4 person：Francesco Cozza 人物身份组登记（2026-10-17）"
    if heading not in text:
        text = text.rstrip() + f"""

{heading}

`cand-0867` C.csv#400 的全名索引项与第5章 p.131 正文全名指向同一人物；Treccani DBI（Ludovica Trezzani，vol. 30，1984）以同名收录卡拉布里亚画家 Francesco Cozza，并记其师从 Domenichino。身份比对与本书的人名、同乡和师承语境相合；外部记录仅作身份佐证，未把生平事实导入[人物卡](../units/persons/francesco-cozza.md)。候选保留 `new` 并映射至该卡。

4条直接 S2 关系候选仍待 S6；祭司群体 `cand-6068` 未分类、祭坛画 `cand-6069` 未消歧、Sassoferrato `cand-2369` 仍待证，Domenichino `cand-0932` 已复用既有 KU。没有新增正式关系。

S4 当前登记 {registered_groups:,} 组／{registered_members:,} 条候选映射；待登记 {pending_groups:,} 组／{pending_members:,} 条映射；KU 总数 {manifest_count:,}。
"""
    return text


def main():
    parser = argparse.ArgumentParser(description="Register the Francesco Cozza S3 identity group as one person KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == MEMBERS[0])
    candidate_rows = [row for row in alignments if row.get("candidate_id") == MEMBERS[0] and not row.get("external_source")]
    external_rows = [row for row in alignments if row.get("candidate_id") == MEMBERS[0] and row.get("external_source") == "Treccani, Dizionario Biografico degli Italiani"]
    card_path = ROOT / CARD_PATH
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    if card_path.exists() and len(candidate_rows) == 1 and candidate_rows[0].get("ku_id") == KU_ID:
        assert any(row["ku_id"] == KU_ID for row in manifest)
        assert CARD_PATH in accepted_text
        assert len(external_rows) == 1 and external_rows[0].get("external_id") == TRECCANI_URL
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}")
        return 0

    assert len(manifest) == 1541, f"unexpected manifest count: {len(manifest)}"
    assert not card_path.exists(), card_path
    assert CARD_PATH not in accepted_text
    assert candidate["suggested_type"] == "person"
    assert len(candidate_rows) == 1, f"expected one candidate alignment row, got {len(candidate_rows)}"
    candidate_alignment = candidate_rows[0]
    assert candidate_alignment["decision"] == "new" and not candidate_alignment.get("ku_id")
    assert get_group(candidate_alignment["resolution_note"]) == GROUP
    assert not external_rows, "Treccani identity row already exists; inspect before retrying"
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)
    assert not any(
        row["type"] == "person"
        and "francesco cozza" in (row["canonical_name"] + " " + row["name_en"]).casefold()
        for row in manifest
    ), "possible same-person KU already exists"

    new_candidates = [row for row in alignments if not row.get("external_source") and row["decision"] == "new"]
    groups = defaultdict(list)
    for row in new_candidates:
        group = get_group(row["resolution_note"])
        assert group, f"new candidate decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
    registered = {group: rows for group, rows in groups.items() if all(row.get("ku_id") for row in rows)}
    pending_groups = {group: rows for group, rows in groups.items() if not any(row.get("ku_id") for row in rows)}
    assert (len(new_candidates), len(groups)) == (4978, 4804)
    assert (len(registered), sum(map(len, registered.values()))) == (522, 652)
    assert GROUP in pending_groups and [row["candidate_id"] for row in pending_groups[GROUP]] == list(MEMBERS)

    statements = {}
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("statement_id") in DIRECT_RELATIONS:
                statements[statement["statement_id"]] = statement
    assert set(statements) == set(DIRECT_RELATIONS)
    assert all((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements.values())
    source_path = ROOT / "02-sources" / "02-Markdown" / "05_CHP-5_sec_i.md"
    assert QUOTE in source_path.read_text(encoding="utf-8-sig")
    assert TRECCANI_URL in s3_resolution(candidate_alignment["resolution_note"])

    planned_alignment = [dict(row) for row in alignments]
    planned_candidate = next(row for row in planned_alignment if row["alignment_id"] == candidate_alignment["alignment_id"])
    planned_candidate["ku_id"] = KU_ID
    planned_candidate["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}"
    planned_candidate["resolution_note"] = s3_resolution(planned_candidate["resolution_note"])
    planned_candidate["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    numeric_ids = [int(row["alignment_id"].removeprefix("aln-")) for row in planned_alignment if row["alignment_id"].removeprefix("aln-").isdigit()]
    planned_alignment.append({
        "alignment_id": f"aln-{max(numeric_ids) + 1:04d}",
        "candidate_id": MEMBERS[0],
        "ku_id": KU_ID,
        "external_source": "Treccani, Dizionario Biografico degli Italiani",
        "external_id": TRECCANI_URL,
        "decision": "same",
        "accessed_date": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
        "legacy_ku_id": "",
        "resolution_note": (
            "Identity corroboration only: Ludovica Trezzani, Dizionario Biografico degli Italiani, vol. 30 (1984), entry ‘COZZA, Francesco’ "
            "names Francesco Cozza as a Calabrian painter and records his pupilage with Domenichino (entry paragraphs 1–2; accessed 2026-10-17). "
            "The full name, regional context, and training context match Haskell ch.5 p.131. This confirms identity only; it does not validate "
            "the source's ‘probably’ recommendation or ‘almost certainly’ association claims and adds no biography or work facts to the KU."
        ),
    })

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": CARD_PATH,
    }]
    assert len(planned_manifest) == 1542
    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if not row.get("external_source") and row["decision"] == "new":
            planned_groups[get_group(row["resolution_note"])].append(row)
    planned_registered = {group: rows for group, rows in planned_groups.items() if all(row.get("ku_id") for row in rows)}
    planned_pending = {group: rows for group, rows in planned_groups.items() if not any(row.get("ku_id") for row in rows)}
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (523, 653)
    assert (len(planned_pending), sum(map(len, planned_pending.values()))) == (4281, 4325)
    for group, rows in planned_registered.items():
        assert len({row["ku_id"] for row in rows}) == 1, group
    pending_new_count = sum(1 for row in planned_alignment if row["decision"] == "new" and not row.get("ku_id"))
    assert pending_new_count == 4340, pending_new_count
    external_count = sum(1 for row in planned_alignment if row.get("external_source"))

    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_PATH}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    process_text = update_process(
        PROCESS_PATH.read_text(encoding="utf-8-sig"),
        len(planned_registered), sum(map(len, planned_registered.values())),
        len(planned_pending), sum(map(len, planned_pending.values())), len(planned_manifest),
    )
    result_text = update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"),
        len(planned_registered), sum(map(len, planned_registered.values())),
        len(planned_pending), sum(map(len, planned_pending.values())), len(planned_manifest),
        len(planned_alignment), external_count, pending_new_count,
    )
    card_text = make_card()

    if args.dry_run:
        print(
            f"dry-run passed: group={GROUP} candidate=1 direct_relation_candidates=4 "
            f"registered_groups_after={len(planned_registered)} mapped_candidates_after={sum(map(len, planned_registered.values()))} "
            f"pending_groups_after={len(planned_pending)} pending_candidates_after={sum(map(len, planned_pending.values()))} "
            f"manifest_after={len(planned_manifest)} alignment_after={len(planned_alignment)} external_records_after={external_count}"
        )
        return 0

    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        f"applied: group={GROUP} ku={KU_ID} candidate=1 direct_relation_candidates=4 "
        f"registered_groups={len(planned_registered)} mapped_candidates={sum(map(len, planned_registered.values()))} "
        f"pending_groups={len(planned_pending)} pending_candidates={sum(map(len, planned_pending.values()))} "
        f"manifest={len(planned_manifest)} alignment={len(planned_alignment)} external_records={external_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
