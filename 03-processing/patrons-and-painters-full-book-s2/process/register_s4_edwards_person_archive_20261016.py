from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

PERSON = {
    "candidate": "cand-0965",
    "group": "new-person:edwards-pietro-4c9347ce42",
    "ku_id": "units/persons/pietro-edwards",
    "card_rel": "04-knowledge/units/persons/pietro-edwards.md",
    "card_path": ROOT / "04-knowledge" / "units" / "persons" / "pietro-edwards.md",
    "type": "person",
    "name_zh": "皮耶特罗·爱德华兹",
    "name_en": "Pietro Edwards",
}
ARCHIVE = {
    "candidate": "cand-8534",
    "group": "archive-group-e755dc71ceb3",
    "ku_id": "units/archives/pietro-edwards-inventories-seminario-patriarcale-ms-788-13",
    "card_rel": "04-knowledge/units/archives/pietro-edwards-inventories-seminario-patriarcale-ms-788-13.md",
    "card_path": ROOT / "04-knowledge" / "units" / "archives" / "pietro-edwards-inventories-seminario-patriarcale-ms-788-13.md",
    "type": "archive",
    "name_zh": "皮耶特罗·爱德华兹编制的清单（Seminario Patriarcale, MSS. 788.13）",
    "name_en": "Pietro Edwards's Inventories (Seminario Patriarcale, MSS. 788.13)",
}

PERSON_STATEMENTS = {
    "st-chp17-p380-edwards-advised-manfrin",
    "st-chp17-p380-manfrin-delegated-picture-selection",
    "st-chp17-p380-manfrin-kept-experts-objections-private",
    "st-chp17-p380-note5-edwards-record",
    "st-chp19-p395-manfrin-confidential-judgment-condition",
    "st-chp19-p395-manfrin-letter-closure-and-signature",
}
ARCHIVE_STATEMENTS = {
    "st-chp9-p261-note2-seminario-edwards-inventories",
    "st-chp17-p380-note5-edwards-record",
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def source(location: str, summary: str, file: str, span: str, quotes: list[tuple[str, str]]):
    return {
        "citation": BOOK,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": quote_span, "text": quote} for quote_span, quote in quotes],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/02-Markdown/{file}",
            "source_span": span,
        },
    }


def frontmatter(title: str, name_en: str, kind: str, sources: list[dict], subtype: str = "") -> str:
    data = {
        "title": title,
        "name_en": name_en,
        "type": kind,
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    if subtype:
        data["sub_type"] = subtype
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)


def person_card() -> str:
    sources = [
        source(
            "第9章；印刷页261；注2；OCR L405",
            "脚注称 Seminario Patriarcale 的 MSS. 788.13 保存 Pietro Edwards 在威尼斯共和国覆亡时编制的清单。",
            "09_CHP-9_intro.md",
            "lines 405; print p. 261, note 2",
            [("lines 405", "where MSS. 788.13 contains those drawn up by Pietro Edwards at the downfall of the Republic.")],
        ),
        source(
            "第17章；印刷页380；OCR L14；注5见 L30",
            "正文称 Pietro Edwards 是 Girolamo Manfrin 的顾问；注5称 Edwards 编制了曼弗林画廊的第一份记录，并将其定位于同一手稿号。",
            "17_CHP-17_sec_i.md",
            "lines 14 and 30; print p. 380",
            [
                ("lines 14", "In a letter to Pietro Edwards, who acted as his adviser"),
                ("lines 30", "The first record of Manfrin’s gallery was made by Pietro Edwards, his adviser, just before the end of the eighteenth century. It exists in manuscript in the Seminario Patriarcale, Venice—MSS. 788.13."),
            ],
        ),
        source(
            "第19章附录；印刷页395；OCR L204–208",
            "附录转录的1793年12月3日信件以 Pietro Edwards 为收信人，并以 Girolamo Manfrin 署名。",
            "19_CHP-19Appendix.md",
            "lines 204–208; print p. 395",
            [("lines 204–208", "Di Casa 3 Xbre 1793 Di V.S. Illma\nDmo Obmo Serv.\nIllmo Sig. Pietro Edwards Girolamo Manfrin.\nVenezia")],
        ),
    ]
    fm = frontmatter(
        f"{PERSON['name_zh']}（{PERSON['name_en']}）",
        PERSON["name_en"],
        "person",
        sources,
    )
    p9 = "[第9章 p.261 注2](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L405）"
    p17 = "[第17章 p.380](../../../02-sources/02-Markdown/17_CHP-17_sec_i.md)（L14、L30）"
    p19 = "[第19章 p.395](../../../02-sources/02-Markdown/19_CHP-19Appendix.md)（L204–208）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应索引人物 Pietro Edwards（索引形式 “Edwards, Pietro”；E.csv#0），正文在第9、17、19章均以全名指称。Haskell 称 Edwards 是 Girolamo Manfrin 的顾问，并报告他编制了曼弗林画廊的第一份记录；第19章附录转录的1793年信件也以 Edwards 为收信人。上述档案与书信内容均按 Haskell 的转录和报告记录，未独立查阅原件。{p9}；{p17}；{p19}

**English:** This card represents the indexed person Pietro Edwards (index form “Edwards, Pietro”; E.csv#0), named in full in Chapters 9, 17, and 19. Haskell identifies Edwards as Girolamo Manfrin’s adviser and reports that he made the first record of the Manfrin gallery; the letter transcribed in the Chapter 19 appendix is also addressed to Edwards. The archival and letter details are recorded as Haskell’s report and transcription; the originals were not independently consulted. {p9}; {p17}; {p19}

### 名称与身份依据

- 索引形式：Edwards, Pietro；索引页码 261n、380、395。索引用于定位，不单独充当人物身份事实。
- 正文锚点：第9章 p.261、第17章 p.380 和第19章 p.395 均明确写出全名 Pietro Edwards；本组依全名及同一书内人物语境归为一人。
- 中文显示名“{PERSON['name_zh']}”为便于阅读的工作音译；未据本书之外材料补充生平或规范身份。

### 语境与边界

第17章将 Edwards 置于 Manfrin 的画作选择与顾问语境中；第19章给出一封由 Haskell 转录的信件结尾，标有1793年12月3日、威尼斯及 Edwards 收信人。第9章和第17章均将 Edwards 与 Seminario Patriarcale 的 MSS. 788.13 相连。书中提及的 Manfrin、该手稿记录及 Edwards 本人分别作为不同对象处理；本卡不补写原书未提供的生卒、职衔或完整履历。

### 内容边界

Haskell 报告 Edwards 曾任 Manfrin 顾问并编制画廊记录；不能据此扩展为持续或独占的顾问关系。第19章文本为书内转录，不能证明原信现状或全部传递史。MSS. 788.13 的手稿与其中记录不并入 Edwards 的人物身份。

## 关系与证据

以下 S2 陈述均标为关系候选，留待 S6 按端点、方向、语境与证据逐条审查；本卡未新增正式关系：

- Edwards 与 Manfrin 的顾问、选画授权和保密语境：`st-chp17-p380-edwards-advised-manfrin`、`st-chp17-p380-manfrin-delegated-picture-selection`、`st-chp17-p380-manfrin-kept-experts-objections-private`、`st-chp19-p395-manfrin-confidential-judgment-condition`、`st-chp19-p395-manfrin-letter-closure-and-signature`。对端为[吉罗拉莫·曼弗林（Girolamo Manfrin）](girolamo-manfrin.md)，均待 S6。
- Edwards 与 MSS. 788.13 档案定位：`st-chp17-p380-note5-edwards-record`；对端为[MSS. 788.13 清单记录](../archives/pietro-edwards-inventories-seminario-patriarcale-ms-788-13.md)，待 S6，原件未查阅。
"""
    return f"---\n{fm}---\n\n{body}"


def archive_card() -> str:
    sources = [
        source(
            "第9章；印刷页261；注2；OCR L405",
            "Haskell 报告威尼斯档案中的 Seminario Patriarcale 藏有 MSS. 788.13，其中包括 Pietro Edwards 在威尼斯共和国覆亡时编制的清单。",
            "09_CHP-9_intro.md",
            "lines 405; print p. 261, note 2",
            [("lines 405", "Others are still unpublished in the Venetian archives, especially those of the Seminario Patriarcale, where MSS. 788.13 contains those drawn up by Pietro Edwards at the downfall of the Republic.")],
        ),
        source(
            "第17章；印刷页380；注5；OCR L30",
            "Haskell 称曼弗林画廊第一份记录由 Pietro Edwards 编制，存在 Seminario Patriarcale 的 MSS. 788.13。",
            "17_CHP-17_sec_i.md",
            "lines 30; print p. 380, note 5",
            [("lines 30", "The first record of Manfrin’s gallery was made by Pietro Edwards, his adviser, just before the end of the eighteenth century. It exists in manuscript in the Seminario Patriarcale, Venice—MSS. 788.13.")],
        ),
    ]
    fm = frontmatter(
        f"{ARCHIVE['name_zh']}（{ARCHIVE['name_en']}）",
        ARCHIVE["name_en"],
        "archive",
        sources,
        subtype="archival record",
    )
    p9 = "[第9章 p.261 注2](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L405）"
    p17 = "[第17章 p.380 注5](../../../02-sources/02-Markdown/17_CHP-17_sec_i.md)（L30）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录 Haskell 所报告的 Seminario Patriarcale, Venice, MSS. 788.13 清单档案定位。第9章称该手稿号包含 Pietro Edwards 在威尼斯共和国覆亡时编制的清单；第17章注5称，曼弗林画廊的第一份记录由 Edwards 编制，约在18世纪末前，并存于同一手稿号。卡名是便于区分的描述性工作题名，不是原手稿题名。手稿、目录和原件均未在本轮独立查阅。{p9}；{p17}

**English:** This card records the archival locator reported by Haskell for Seminario Patriarcale, Venice, MSS. 788.13. Chapter 9 says this manuscript number contains inventories drawn up by Pietro Edwards at the downfall of the Venetian Republic. Chapter 17, note 5, says the first record of the Manfrin gallery was made by Edwards shortly before the end of the eighteenth century and is held under the same manuscript number. The card title is a descriptive working label, not an original manuscript title. The manuscript, catalogue, and original record were not independently consulted in this pass. {p9}; {p17}

### 名称与定位

- 描述性工作题名：{ARCHIVE['name_en']}；不作为原题名或正式目录著录。
- 保管机构和定位：Seminario Patriarcale, Venice；MSS. 788.13；仅按 Haskell 书内报告记录。
- 类型：手稿档案记录定位。第9章以复数称清单，第17章明确提到曼弗林画廊“第一份记录”；本卡保留两处报告，不据此推断手稿全貌、完整内容或所有记录之间的关系。
- 记录者：Pietro Edwards；为书中所述，不代表原件已核。
- 时间：第9章称“at the downfall of the Republic”，第17章称“just before the end of the eighteenth century”；保留两种原书措辞，不进一步换算为精确年份。

### 内容边界

本卡不把整组威尼斯清单、Manfrin 的全部藏品记录或未提及的馆藏目录并入该定位；也不推定现行馆藏状态、档案全宗层级、原件题名、卷内件数或数字化链接。两个出处共享 MSS. 788.13 定位，但本轮没有通过目录或原件确认其具体物理对应关系。

## 关系与证据

S2 将该定位与 Pietro Edwards 及 Manfrin 画廊记录相连；具体创制者、档案保存和记录内容关系均留待 S6 审查，本卡未新增正式关系。

- `st-chp9-p261-note2-seminario-edwards-inventories`、`st-chp17-p380-note5-edwards-record` 将该定位与[皮耶特罗·爱德华兹（Pietro Edwards）](../persons/pietro-edwards.md)相连；关系类型与范围待 S6，依据为 Haskell 报告，原件未查阅。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Pietro Edwards person and MSS. 788.13 archive identity groups in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    decision_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert PERSON["candidate"] in candidate_by_id
    assert candidate_by_id[PERSON["candidate"]]["suggested_type"] == "person"
    assert candidate_by_id[PERSON["candidate"]]["canonical_name"] == "Edwards, Pietro"
    assert ARCHIVE["candidate"] in candidate_by_id
    assert candidate_by_id[ARCHIVE["candidate"]]["suggested_type"] == "archive"
    assert "788.13" in candidate_by_id[ARCHIVE["candidate"]]["canonical_name"]

    for item in (PERSON, ARCHIVE):
        decision = decision_by_id[item["candidate"]]
        assert decision["decision"] == "new" and not decision.get("ku_id"), item["candidate"]
        assert sync.get_group(decision.get("resolution_note", "")) == item["group"]
        group_members = [
            row for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == item["group"]
        ]
        assert [row["candidate_id"] for row in group_members] == [item["candidate"]]
        assert not item["card_path"].exists(), item["card_path"]
        assert item["card_rel"] not in accepted
        assert not any(row.get("ku_id") == item["ku_id"] or row.get("card_path") == item["card_rel"] for row in manifest)
        assert not any(
            row["type"] == item["type"]
            and (row.get("name_en", "").casefold() == item["name_en"].casefold()
                 or row.get("canonical_name", "").casefold() == item["name_zh"].casefold())
            for row in manifest
        ), f"duplicate same-title KU: {item['ku_id']}"

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    person_direct = {
        row["statement_id"] for row in statements
        if PERSON["candidate"] in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    }
    archive_direct = {
        row["statement_id"] for row in statements
        if ARCHIVE["candidate"] in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    }
    assert person_direct == PERSON_STATEMENTS, person_direct ^ PERSON_STATEMENTS
    assert archive_direct == ARCHIVE_STATEMENTS, archive_direct ^ ARCHIVE_STATEMENTS
    relation_count = sum(
        row.get("qualifiers", {}).get("relation_candidate") is True
        for row in statements if row["statement_id"] in PERSON_STATEMENTS | ARCHIVE_STATEMENTS
    )
    assert relation_count == len(PERSON_STATEMENTS | ARCHIVE_STATEMENTS)

    source_files = {
        "09_CHP-9_intro.md": ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md",
        "17_CHP-17_sec_i.md": ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_i.md",
        "19_CHP-19Appendix.md": ROOT / "02-sources" / "02-Markdown" / "19_CHP-19Appendix.md",
    }
    quotes = [
        ("09_CHP-9_intro.md", "where MSS. 788.13 contains those drawn up by Pietro Edwards at the downfall of the Republic."),
        ("17_CHP-17_sec_i.md", "In a letter to Pietro Edwards, who acted as his adviser"),
        ("17_CHP-17_sec_i.md", "The first record of Manfrin’s gallery was made by Pietro Edwards, his adviser, just before the end of the eighteenth century. It exists in manuscript in the Seminario Patriarcale, Venice—MSS. 788.13."),
        ("19_CHP-19Appendix.md", "Illmo Sig. Pietro Edwards Girolamo Manfrin."),
    ]
    for filename, quote in quotes:
        assert quote in source_files[filename].read_text(encoding="utf-8-sig"), (filename, quote)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for item in (PERSON, ARCHIVE):
        planned_by_id[item["candidate"]]["ku_id"] = item["ku_id"]
        planned_by_id[item["candidate"]]["resolution_note"] += (
            f" S4 registration: mapped {item['group']} to {item['ku_id']}."
        )
    planned_manifest = list(manifest)
    for item in (PERSON, ARCHIVE):
        planned_manifest.append({
            "ku_id": item["ku_id"],
            "type": item["type"],
            "canonical_name": item["name_zh"],
            "name_en": item["name_en"],
            "source_task": TASK,
            "card_path": item["card_rel"],
        })

    stats = sync.summarize_by_type(candidate_rows, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidate_by_id)
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_note = (
        "\n\n### S4：Pietro Edwards 人物与 MSS. 788.13 档案端点登记（2026-10-16）\n\n"
        f"人物组 `{PERSON['group']}`（`{PERSON['candidate']}`）映射至[皮耶特罗·爱德华兹人物卡]"
        "(../../../04-knowledge/units/persons/pietro-edwards.md)；"
        f"档案组 `{ARCHIVE['group']}`（`{ARCHIVE['candidate']}`）映射至[Edwards 清单档案卡]"
        "(../../../04-knowledge/units/archives/pietro-edwards-inventories-seminario-patriarcale-ms-788-13.md)。"
        "第9章 p.261 与第17章 p.380 均报告 Seminario Patriarcale 的 MSS. 788.13 与 Edwards 清单/曼弗林画廊记录有关；"
        "两处报告的时间措辞分别保留为“威尼斯共和国覆亡时”和“18世纪末前”，本轮未把它们换算为精确年份。"
        "手稿、目录和原件均未独立查阅，卡名为描述性工作题名。"
        f"Edwards 的6条直接关系候选及档案端点的2条关系候选全部保留待 S6；Manfrin 人物端点已映射，本轮未修改 `relations.csv`。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_note = (
        "\n\n### S4：Pietro Edwards 跨章人物与档案端点登记（2026-10-16）\n\n"
        f"人物候选 `{PERSON['candidate']}` 登记为[皮耶特罗·爱德华兹人物卡](../units/persons/pietro-edwards.md)；"
        f"档案候选 `{ARCHIVE['candidate']}` 登记为[MSS. 788.13 清单档案卡]"
        "(../units/archives/pietro-edwards-inventories-seminario-patriarcale-ms-788-13.md)。"
        "p.261 与 p.380 共享手稿号，但原件和目录未查阅；档案描述不等同于原题或完整目录著录，时间保持书内模糊表述。"
        "6条人物关系候选和2条档案关系候选待 S6，未写入正式边；Girolamo Manfrin 人物端点已登记。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    process_text += process_note
    result_text += result_note

    if args.dry_run:
        print("S4 Edwards registration dry-run passed")
        print(f"person: {PERSON['candidate']} -> {PERSON['ku_id']} ({len(person_direct)} direct statements)")
        print(f"archive: {ARCHIVE['candidate']} -> {ARCHIVE['ku_id']} ({len(archive_direct)} direct statements)")
        print(f"relation candidates retained for S6: {relation_count}; formal relation writes: 0")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted paths unique")
        print(
            f"registered={sync.fmt(totals['registered_groups'])} groups/{sync.fmt(totals['registered_members'])} candidates; "
            f"pending={sync.fmt(totals['pending_groups'])} groups/{sync.fmt(totals['pending_members'])} candidates"
        )
        print("group membership, source quotations, candidate types, destination uniqueness, and direct endpoints checked; no files changed")
        return 0

    PERSON["card_path"].write_text(person_card(), encoding="utf-8-sig", newline="\n")
    ARCHIVE["card_path"].write_text(archive_card(), encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    for item in sorted((PERSON, ARCHIVE), key=lambda record: record["card_rel"]):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > item["card_rel"]),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {item['card_rel']}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: person={PERSON['ku_id']}; archive={ARCHIVE['ku_id']}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
