from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml
import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"

CANDIDATES = ("cand-2122", "cand-2123")
GROUP = "sg3-institution-remondini"
KU_ID = "units/institutions/remondini-firm"
CARD_REL = "04-knowledge/units/institutions/remondini-firm.md"
NAME_ZH = "伦多尼印刷商行"
NAME_EN = "Remondini firm"

SOURCES = (
    {
        "chapter": "13",
        "page": "340",
        "file": "13_CHP-13_intro.md",
        "lines": "83-85",
        "quote": (
            "the firm of Remondini which was established at Bassano, but which had a branch in Venice.2 "
            "The Remondini also published books, but the main activity . of the firm lay in issuing separate prints. "
            "On the whole their market was restricted to a very different public from that of the great enterprises "
            "that have been discussed so far. They specialised in cheap romantic novels and in devotional prints to "
            "be hung up in peasants’ houses; but towards the middle of the eighteenth century they greatly expanded "
            "and began to acquire an international clientèle. This brought them into rivalry with the more established "
            "institutions which greeted their appearance on the scene with bitter hostility, the more so as the "
            "Remondini had few scruples about producing facsimiles of other publications at much reduced prices. "
            "As the firm grew richer it was able to employ not only some of the best printers but also many leading "
            "artists to produce paintings and drawings for extensive reproduction. Piazzetta, Amigoni, Guarana and, "
            "above all, Pietro Longhi were popularised by the Remondini in this way.3"
        ),
        "summary": "第十三章称 Remondini 为设于 Bassano、在 Venice 有分支的印刷商行；其业务包括出版图书，主要发行单张版画，并经营廉价爱情小说、宗教版画及低价仿印；哈斯克尔称该行在十八世纪中叶前后扩展并开始取得国际客户。",
        "note": "Haskell’s description; OCR punctuation retained in the quoted phrase ‘activity .’",
    },
    {
        "chapter": "15",
        "page": "367",
        "file": "15_CHP-15_sec_ii.md",
        "lines": "94",
        "quote": "Bassano [Remondini], 1787.",
        "summary": "第十五章注2将一部 1787 年在 Bassano 出版的书目项标作 [Remondini]；方括号中的出版者说明按 Haskell 的书目指称记录，未独立查阅该版。",
        "note": "note 2; publisher/imprint attribution in Haskell’s bibliography, edition not independently consulted",
    },
)


def read_csv(path):
    return card_writer.read_csv(path)


def write_csv(path, fields, rows):
    card_writer.write_csv(path, fields, rows)


def make_card():
    source_rows = []
    for item in SOURCES:
        source_rows.append({
            "citation": card_writer.BOOK_CITATION,
            "location": f"第{item['chapter']}章；印刷页{item['page']}；OCR L{item['lines']}"
            + (f"；{item['note']}" if item["note"] else ""),
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": f"lines {item['lines']}; print p. {item['page']}"
                + (f"; {item['note']}" if item["note"] else ""),
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "institution",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ev13 = "[第十三章 p.340](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L83–85）"
    ev15 = "[第十五章 p.367 注2](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)（L94）"
    body = f"""## 内容

### 描述

**中文：** 哈斯克尔称 Remondini 为设于 Bassano、在 Venice 设有分支的印刷商行。第十三章称其出版图书，但主要业务是发行单张版画，并提到廉价爱情小说、供农民家庭悬挂的宗教版画、低价仿印及为版画复制提供图像的活动；哈斯克尔还称该行在十八世纪中叶前后扩展并开始拥有国际客户。以上均为原书陈述，不是本轮对机构沿革、出版物或市场范围的独立核验。中文名称为工作译名，不宣称官方译名。{ev13}

**English:** Haskell describes Remondini as a printing and publishing firm established at Bassano with a branch in Venice. Chapter 13 says it published books but mainly issued separate prints, and refers to cheap romantic novels, devotional prints for peasant homes, low-priced facsimiles, and the production of images for reproductive printing; Haskell also says the firm expanded and began to acquire an international clientele around the middle of the eighteenth century. These are statements in the book, not independent verification of the firm's history, publications, or market. The Chinese name is a working translation, not an asserted official name. {ev13}

### 名称

- 中文显示名（工作译名）：{NAME_ZH}；不宣称官方中文名。{ev13}
- 书中名称：Remondini、the firm of Remondini、the Remondini。{ev13}
- 机构性质：印刷商行；书中同时记载出版图书及主要发行单张版画。{ev13}

### 地点与书目指称

- 设立地：Bassano。{ev13}
- 分支地点：Venice；书中称该行在此设有分支。{ev13}
- 出版者／印记形式：Bassano [Remondini], 1787；Haskell 书目中的出版者指称，所列版本未独立查阅。{ev15}

### 本书相关内容

第十三章 p.340 将印刷商行、其出版和印刷活动及艺术家复制版画的语境相连；第十五章 p.367 注2另以 [Remondini] 标示一项 Bassano 1787 年书目出版者。两处按 S3 跨章组归为同一书中所指机构。本卡不据此扩展为 Remondini 家族全体或具体成员的身份判断。

## 关系与证据

### 关系记录

当前没有正式关系。S2 对这组记录20条直接陈述，其中16条为关系候选；人物、作品、地点及出版活动端点均保留在原断言中，待 S6 逐条审查。本次只登记机构身份，不创建正式关系。相关“低价仿印”程序另见[伦多尼印制低价仿本](../procedures/remondini-low-priced-facsimiles.md)，该程序卡不与本机构合并。
"""
    return f"---\n{fm}---\n\n{body}"


def count_groups(rows):
    groups = defaultdict(list)
    for row in rows:
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new":
            group = card_writer.get_group(row["resolution_note"])
            assert group, f"new decision lacks group: {row['candidate_id']}"
            groups[group].append(row)
    registered = {group: members for group, members in groups.items() if any(row.get("ku_id") for row in members)}
    mapped = sum(bool(row.get("ku_id")) for members in registered.values() for row in members)
    return len(registered), mapped, len(groups) - len(registered), sum(
        row.get("decision") == "new" and not row.get("ku_id") and not row.get("external_source") for row in rows
    )


def update_result(result, manifest_count, registered, mapped, pending_groups, pending_members):
    pattern = re.compile(
        r"S4 已登记\s*[\d,]+组、映射[\d,]+条成员候选；尚待登记[\d,]+组、[\d,]+条映射。"
    )
    result, n = pattern.subn(
        f"S4 已登记{registered:,}组、映射{mapped:,}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。",
        result,
        count=1,
    )
    assert n == 1, "could not update current S4 summary in result"
    manifest_pattern = re.compile(r"(\|\s*\[KU 登记\]\(\.\./tables/ku-manifest\.csv\)\s*\|\s*)[\d,]+ KU")
    result, n = manifest_pattern.subn(lambda m: f"{m.group(1)}{manifest_count:,} KU", result, count=1)
    assert n == 1, "could not update manifest total in result"
    return result


def main():
    parser = argparse.ArgumentParser(description="Register the cross-chapter Remondini institution group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    align_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    card_path = ROOT / CARD_REL
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert set(CANDIDATES) <= candidate_by_id.keys()
    assert all(candidate_by_id[c]["suggested_type"] == "institution" for c in CANDIDATES)
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and card_writer.get_group(row["resolution_note"]) == GROUP
    ]
    assert sorted(row["candidate_id"] for row in group_rows) == sorted(CANDIDATES)
    assert all(not row.get("ku_id") for row in group_rows)
    assert not card_path.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert CARD_REL not in accepted

    mentions = [row for row in read_csv(TABLES / "mentions.csv")[1] if row.get("candidate_id") in CANDIDATES]
    assert len(mentions) == 14, f"unexpected mention count: {len(mentions)}"
    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in CANDIDATES or row.get("object_candidate_id") in CANDIDATES
    ]
    direct_relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate")]
    assert len(direct) == 20, f"unexpected direct statement count: {len(direct)}"
    assert len(direct_relations) == 16, f"unexpected direct relation candidate count: {len(direct_relations)}"

    for item in SOURCES:
        source = ROOT / "02-sources" / "02-Markdown" / item["file"]
        text = " ".join(source.read_text(encoding="utf-8-sig").split())
        quote = " ".join(item["quote"].split())
        assert quote in text, (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for candidate_id in CANDIDATES:
        planned_by_id[candidate_id]["ku_id"] = KU_ID
        planned_by_id[candidate_id]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "institution",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    registered, mapped, pending_groups, pending_members = count_groups(planned_alignment)
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    result_text = update_result(result_text, len(planned_manifest), registered, mapped, pending_groups, pending_members)

    process_note = (
        "\n\n### S4 institution：Remondini 跨章身份组登记（2026-10-16）\n\n"
        f"`{CANDIDATES[0]}`（Q-R.csv#49，第15章书目出版者指称）与 `{CANDIDATES[1]}`（Q-R.csv#50，第13章印刷商行）"
        f"均映射至[伦多尼印刷商行机构卡](../../../04-knowledge/units/institutions/remondini-firm.md)。"
        "第13章称其设于 Bassano、在 Venice 有分支并从事印刷出版；第15章 p.367 注2列有 Bassano [Remondini], 1787。"
        "后者按 Haskell 书目指称记录，未独立查阅该版。S2 共有20条直接陈述，其中16条是关系候选，全部留待 S6；"
        "不扩展为 Remondini 家族成员身份，不新增正式关系，也未进行外部核验或 S5 补足。"
        f"S4 累计登记{registered:,}组/{mapped:,}条成员映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    result_note = (
        "\n\n### institution：Remondini 跨章身份组 S4 登记（2026-10-16）\n\n"
        "`cand-2122` 与 `cand-2123` 共同映射至[伦多尼印刷商行机构卡](../units/institutions/remondini-firm.md)。"
        "第13章的机构叙述与第15章书目中的 Bassano [Remondini], 1787 指称保留各自来源限定；"
        "未独立查阅被引版本。20条直接断言中的16条关系候选留待 S6。"
        f"全书 S4 当前登记{registered:,}组/{mapped:,}条映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    process_text += process_note
    result_text += result_note

    if args.dry_run:
        print(f"S4 institution dry-run passed: {CANDIDATES} -> {KU_ID}")
        print(f"mentions={len(mentions)}; direct statements={len(direct)}; relation candidates={len(direct_relations)}")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted path unique")
        print(f"registered={registered:,} groups/{mapped:,} candidates; pending={pending_groups:,} groups/{pending_members:,} candidates")
        print("both source quotations checked; no files changed")
        return 0

    card_path.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATES} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={registered:,}/{mapped:,}; pending={pending_groups:,}/{pending_members:,}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
