from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
CANDIDATE = "cand-1379"
GROUP = "new-person:legros-pierre-304dcc72bb"
KU_ID = "units/persons/pierre-ii-legros"
CARD = "04-knowledge/units/persons/pierre-ii-legros.md"
TRECCANI = "https://www.treccani.it/enciclopedia/pierre-i-legros_%28Enciclopedia-Italiana%29/"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCES = (
    {
        "location": "第3章，印刷页92；OCR L173–174",
        "summary": "Haskell称法国雕塑家 Pierre Legros 是圣依纳爵祭坛圣人像竞赛的获胜者，并记述法国学生称其 Monsu Le Gros；随后称他为法国学院学生及法国国王供养的 pensioner。",
        "file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
        "span": "lines 173–174; print p. 92",
        "quotes": [
            (
                "lines 173–174",
                "Frenchman Pierre Legros. While the voting took place crowds waited impatiently in the Casa Professa, and when the decision was announced, French students carried him through the streets in triumph, shouting ‘Viva, viva, Monsu Le Gros.’ The authorities of the French Academy in Rome, where Legros was a student, were less enthusiastic, and after he had also agreed to make a large marble group of Religion triumphing over Heresy to be placed on one side of the altar, he was dismissed for accepting private commissions in defiance of his status as a pensioner of the King of France.",
            )
        ],
    },
    {
        "location": "第3章，印刷页93；OCR L185–186",
        "summary": "Haskell在圣依纳爵堂的语境中再次称 Legros 完成一件祭坛浮雕，并于1710年完成教宗 Gregory XV 与 Cardinal Ludovisi 的纪念碑。",
        "file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
        "span": "lines 185–186; print p. 93",
        "quotes": [
            ("lines 185", "In 1697 Padre Pozzo designed an altar in the left transept of S. Ignazio which Legros completed with an appealing bas-relief representing The Assumption of the Blessed Luigi Gonzaga."),
            ("lines 186", "In 1710 Pierre Legros completed the monument to Pope Gregory XV and Cardinal Ludovisi in the same church."),
        ],
    },
    {
        "location": "第20章后记，印刷页400；OCR L47",
        "summary": "Haskell在讨论圣依纳爵堂的研究时再次提及 Legros 的雕像，语境与第3章的罗马耶稣会工作一致。",
        "file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "span": "line 47; print p. 400",
        "quotes": [
            ("line 47", "the statues by Théodon and Legros in the church—and thus to our knowledge of Jesuit patronage in general."),
        ],
    },
)


def book_source(item: dict) -> dict:
    return {
        "citation": BOOK,
        "location": item["location"],
        "sentence_summary": item["summary"],
        "original_quotes": [
            {"source_span": span, "text": quote} for span, quote in item["quotes"]
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": item["file"],
            "source_span": item["span"],
        },
    }


def make_card() -> str:
    sources = [book_source(item) for item in SOURCES]
    sources.append(
        {
            "citation": f'Treccani, “LEGROS, Pierre I,” *Enciclopedia Italiana*. {TRECCANI}. Accessed 2026-10-16.',
            "location": "词条“Il figlio, Pierre II”段",
            "sentence_summary": "条目将 Pierre II 识别为 Pierre I 之子，称其为雕塑家与建筑师，生于巴黎、卒于罗马，并记其在罗马为耶稣会工作；用于与父亲 Pierre I 区分，不据此补录完整生平。",
        }
    )
    frontmatter = {
        "title": "皮埃尔·勒格罗斯二世（Pierre II Legros）",
        "name_en": "Pierre II Legros",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p92 = "[第3章 p.92](../../../02-sources/02-Markdown/03_CHP-3_sec_iv.md)（L173–174）"
    p93 = "[第3章 p.93](../../../02-sources/02-Markdown/03_CHP-3_sec_iv.md)（L185–186）"
    p400 = "[第20章后记 p.400](../../../02-sources/02-Markdown/20_CHP-20Postscript.md)（L47）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应哈斯克尔第3章所称的法国雕塑家 Pierre Legros，并与第20章后记中圣依纳爵堂语境下的 Legros 合并为同一人物。Treccani 将 Pierre II 与其父、法国宫廷雕塑家 Pierre I 区分；其所述 Pierre II 在罗马为耶稣会工作的身份，与哈斯克尔所记法国学院学生及耶稣会雕塑家语境吻合。此处只处理人物身份，不把具名作品并入人物卡。{p92}；{p93}；{p400}

**English:** This unit represents the French sculptor Pierre Legros named in Haskell’s Chapter 3 and the Legros mentioned in the Jesuit context of the Chapter 20 postscript as one person. Treccani distinguishes Pierre II from his father, the court sculptor Pierre I; its account of Pierre II working for the Jesuits in Rome matches Haskell’s references to a student at the French Academy and a principal Jesuit sculptor. This record addresses person identity only; named works remain separate from the person. {p92}; {p93}; {p400}

### 名称与身份

- 规范展示名：Pierre II Legros／皮埃尔·勒格罗斯二世。Treccani 将此人称为 Pierre II，用以区别其父 Pierre I。
- 书内名称：Pierre Legros、Legros；“Monsu Le Gros”见第3章法国学生庆贺获胜的引语。该拼写作为书内异名，不替代规范展示名。{p92}；{p93}；{p400}
- 身份：法国雕塑家；Haskell 称其为法国学院学生、法国国王供养的 pensioner，并称其后来成为耶稣会的主要雕塑家。该人物标签依书内说法保留，不扩展为完整履历。{p92}
- 身份辨析：Treccani 的 Pierre I 条目将父亲（1629–1714）与儿子 Pierre II（1666–1719）分别说明；本组依据 Haskell 的罗马法国学院与耶稣会工作语境对应后者。该外部来源只用于身份区分与核对，不表示卡内其他事实均已外部验证。[Treccani：LEGROS, Pierre I](<{TRECCANI}>)

### 跨章身份依据

第3章记 Pierre Legros 获得圣依纳爵雕像竞赛，并在同段说明其法国学院学生身份；第3章 p.93 再以 Legros 与 Pierre Legros 指称圣依纳爵堂工作中的同一雕塑家。后记 p.400 在该堂艺术研究语境中再次提及 Legros。以上书内交叉语境与 Treccani 的父子区分共同支持该单一人物组；不据此为书内提及建立额外作品清单。{p92}；{p93}；{p400}

## 关系与证据

### 身份与外部链接

[Treccani：LEGROS, Pierre I](<{TRECCANI}>)（词条在 Pierre I 条目下区分其子 Pierre II；用于人物身份辨析。）

### 关系记录

`cand-1379` 在第3章的11条直接 S2 陈述均标为关系候选，仍逐条留待 S6；本次未写入正式关系。其他候选端点、作品身份与关系方向须在 S6 按其自身证据裁决。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Pierre II Legros as one S4 person identity group.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE)
    decision_rows = [
        row for row in alignments
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    ]
    assert len(decision_rows) == 1
    decision = decision_rows[0]
    assert candidate["suggested_type"] == "person"
    assert decision["decision"] == "new" and not decision.get("ku_id")
    assert sync.get_group(decision.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert not (ROOT / CARD).exists()
    assert CARD not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD for row in manifest)
    assert not any(row.get("external_source") == "Treccani Enciclopedia Italiana" and row.get("candidate_id") == CANDIDATE for row in alignments)

    for item in SOURCES:
        normalized = " ".join((ROOT / item["file"]).read_text(encoding="utf-8-sig").split())
        for _, quote in item["quotes"]:
            assert " ".join(quote.split()) in normalized, (item["file"], quote)

    statements = sync.load_statements()
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    relation_candidates = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate")]
    assert len(direct) == 11 and len(relation_candidates) == 11, (len(direct), len(relation_candidates))

    planned_alignment = [dict(row) for row in alignments]
    next_alignment_number = max(int(row["alignment_id"].removeprefix("aln-")) for row in alignments if row.get("alignment_id")) + 1
    decision = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    decision["ku_id"] = KU_ID
    decision["resolution_note"] += (
        f" S3 identity check 2026-10-16: Treccani distinguishes Pierre II from Pierre I and describes Pierre II's Roman Jesuit work; "
        f"this matches the Haskell context. Identity only; see alignment aln-{next_alignment_number}."
        f" S4 registration: mapped {GROUP} to {KU_ID}."
    )
    external_row = {
        "alignment_id": f"aln-{next_alignment_number}",
        "candidate_id": CANDIDATE,
        "ku_id": KU_ID,
        "external_source": "Treccani Enciclopedia Italiana",
        "external_id": TRECCANI,
        "decision": "same",
        "accessed_date": "2026-10-16",
        "process_ref": "S3-full-book-2026-10-16",
        "legacy_ku_id": "",
        "resolution_note": "Identity only: the Pierre I entry distinguishes his son Pierre II (Paris 1666–Rome 1719), a sculptor and architect who worked for the Jesuits in Rome. This fits Haskell's French Academy and Jesuit-work context; it does not verify all book claims. Accessed 2026-10-16.",
    }
    planned_alignment.append(external_row)
    planned_manifest = list(manifest)
    planned_manifest.append(
        {
            "ku_id": KU_ID,
            "type": "person",
            "canonical_name": "皮埃尔·勒格罗斯二世",
            "name_en": "Pierre II Legros",
            "source_task": TASK,
            "card_path": CARD,
        }
    )

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    external_count = sum(bool(row.get("external_source")) for row in planned_alignment)
    alignment_count = len(planned_alignment)
    current_status = (
        f"**当前状态：全书 S2 语义处理已完成，尚未独立语义验收；S3 候选决定记录已按收口标准完成台账核对，"
        f"{sync.fmt(totals['total'])} 个候选均有唯一决定、说明与过程引用。{sync.fmt(totals['undecided'])} 项仍作为明确待证对象保留，"
        f"不将台账收口表述为身份问题全部解决；S4 KU 登记处理中。** "
        f"{sync.fmt(totals['total'])} 个候选决定行中，same={sync.fmt(totals['same_candidates'])}（指向{sync.fmt(totals['same_kus'])}个既有 KU）、"
        f"new={sync.fmt(totals['new_candidates'])}（{sync.fmt(totals['new_groups'])}个身份组）、conflict={sync.fmt(totals['conflict'])}、"
        f"excluded={sync.fmt(totals['excluded'])}、undecided={sync.fmt(totals['undecided'])}。"
        f"S4 已登记{sync.fmt(totals['registered_groups'])}组、映射{sync.fmt(totals['registered_members'])}条成员候选；"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组、{sync.fmt(totals['pending_members'])}条映射。"
    )
    result_text, n = re.subn(r"^\*\*当前状态：.*?S3 已将", current_status + "S3 已将", result_text, count=1, flags=re.M)
    assert n == 1
    result_text, n = re.subn(
        r"^\| \[全书对齐\].*$",
        f"| [全书对齐](../tables/alignment.csv) | {sync.fmt(alignment_count)} 条：{sync.fmt(totals['total'])} 条候选决定记录及 {sync.fmt(external_count)} 条外部标识记录；候选决定数见下表 |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert n == 1
    result_text, n = re.subn(r"现共\d+条；这些记录不作为额外候选计数。", f"现共{sync.fmt(external_count)}条；这些记录不作为额外候选计数。", result_text, count=1)
    assert n == 1
    result_text, n = re.subn(r"\d+条外部标识行另计、不纳入候选数。", f"{sync.fmt(external_count)}条外部标识行另计、不纳入候选数。", result_text, count=1)
    assert n == 1
    result_text = result_text.replace("5,541 条 undecided", f"{sync.fmt(totals['undecided'])} 条 undecided")
    result_text += (
        "\n\n### person：Pierre II Legros 跨章人物组 S4 登记（2026-10-16）\n\n"
        "`cand-1379`（L.csv#36）登记至[皮埃尔·勒格罗斯二世人物卡](../../04-knowledge/units/persons/pierre-ii-legros.md)。第3章 pp.92–93 与第20章后记 p.400 的 Legros 语境相互衔接；Treccani 区分 Pierre I 与其子 Pierre II，并将后者置于罗马耶稣会工作语境，支持本组与后者对应。新增 Treccani 身份记录 aln-"
        f"{next_alignment_number}；仅核对人物身份，不扩展为完整生平。该候选11条直接 S2 陈述均为关系候选，全部留待 S6；未登记正式关系或开展 S5。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S4 person：Pierre II Legros 跨章人物组登记（2026-10-16）\n\n"
        "`cand-1379`（L.csv#36）按 `new-person:legros-pierre-304dcc72bb` 登记为一张人物 KU。第3章 p.92 称 Pierre Legros 为法国人，记其赢得圣依纳爵堂祭坛雕像竞赛、法国学院学生身份及法国国王供养人身份；p.93 以 Legros／Pierre Legros 记其在 S. Ignazio 的工作；第20章后记 p.400 再提到该堂的 Legros。Treccani 的 Pierre I 条目区分其子 Pierre II（1666–1719），并记其在罗马为耶稣会工作；与书内语境吻合。该外部来源仅用于父子身份辨析，未据此补入完整生卒履历。"
        "新增 alignment 外部身份记录用于 Treccani 匹配；原 S3 `new` 决定及身份组保持不变。11条直接 S2 陈述全部为关系候选，仍留待 S6；本次不登记作品端点、正式关系或 S5 补足。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )

    if args.dry_run:
        print("S4 Pierre II Legros dry-run passed:")
        print(f"  {CANDIDATE} -> {KU_ID}; group={GROUP}")
        print(f"  direct S2 statements={len(direct)}; relation candidates={len(relation_candidates)}")
        print(f"  manifest={len(manifest):,} -> {len(planned_manifest):,}; alignment={len(alignments):,} -> {alignment_count:,}; accepted path unique")
        print(f"  registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}")
        return 0

    (ROOT / CARD).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / CARD).write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(ALIGNMENT, alignment_fields, planned_alignment)
    sync.write_csv(MANIFEST, manifest_fields, planned_manifest)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD}")
    ACCEPTED.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied S4 registration; manifest={len(planned_manifest):,}; pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; alignment={alignment_count:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
