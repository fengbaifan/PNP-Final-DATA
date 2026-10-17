from __future__ import annotations

import argparse
import csv
import hashlib
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
SOURCES_PATH = TABLES / "sources.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
TRECCANI_URL = "https://www.treccani.it/enciclopedia/stato-pontificio/"
TRECCANI_ID = "src-" + hashlib.sha256(TRECCANI_URL.encode("utf-8")).hexdigest()[:16]
TRECCANI_CITATION = (
    "Treccani, ‘Pontificio, Stato,’ Enciclopedia on line. "
    f"{TRECCANI_URL} Accessed 2026-10-17."
)
GROUP = "sg3-institution-cand-1831"
KU_ID = "units/institutions/papal-states"
CARD_REL = "04-knowledge/units/institutions/papal-states.md"
CARD_PATH = ROOT / "04-knowledge" / "units" / "institutions" / "papal-states.md"
CANDIDATES = ("cand-1831", "cand-1832", "cand-1833")
RELATION_STATEMENTS = {
    "st-chp2-sec-ii-l10-18-urban-professed-wealth-policy",
    "st-chp2-sec-ii-l10-18-urban-role-absolute-monarch",
    "st-chp2-sec-ii-l10-18-venetian-income-estimate",
    "st-chp2-sec-ii-l3-8-sovereignty",
    "st-chp2-secii-l42-50-cost_reported",
    "st-chp6-p146-castro-papal-territory",
    "st-chp6-p149-italian-economic-collapse",
    "st-chp8-p203-bologna-second-capital",
}
NON_RELATION_STATEMENTS = {
    "st-chp2-sec-ii-l10-18-papal-states-wealth-at-accession",
    "st-chp6-p162-v1-05",
}
ITEM = {
    "ku_id": KU_ID,
    "card_rel": CARD_REL,
    "type": "institution",
    "name_zh": "教皇国",
    "name_en": "Papal States",
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


def card_text() -> str:
    sources = [
        {
            "citation": BOOK,
            "location": "第2章；印刷页31；OCR L3–8",
            "sentence_summary": "Haskell 将 Urban VIII 对“the state”的统治写成最高权力；S2 语境将该政治地域映射至 Papal States。",
            "original_quotes": [{"source_span": "line 3", "text": "the supreme power in the state"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                "source_span": "lines 3–8; print p. 31",
            },
        },
        {
            "citation": BOOK,
            "location": "第2章；印刷页32；OCR L10–18",
            "sentence_summary": "正文称 Papal States 在 Urban VIII 即位时“足够富裕”；威尼斯使节的年收入估值为转述估值，未独立核实。",
            "original_quotes": [
                {"source_span": "line 12", "text": "the papal states were rich enough"},
                {"source_span": "lines 12–13", "text": "Venetian ambassadors estimated their income to be two million scudi a year"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                "source_span": "lines 10–18; print p. 32",
            },
        },
        {
            "citation": BOOK,
            "location": "第2章；印刷页35；OCR L42–50",
            "sentence_summary": "Haskell 将圣彼得大殿青铜华盖的造价报告为200,000 scudi、约为教皇国年收入十分之一；印刷页读数与 OCR 不同，细节仍属作者报告。",
            "original_quotes": [{"source_span": "line 47", "text": "The cost had been enormous—200,000 scudi or a tenth of the annual income of the papal states"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                "source_span": "lines 42–50; print p. 35 (print correction recorded in S2)",
            },
        },
        {
            "citation": BOOK,
            "location": "第6章；印刷页146、149；OCR L6、43",
            "sentence_summary": "Haskell 分别称 Castro 位于教皇领地内，并称教皇国日益受到意大利经济整体衰退影响；前者区分城市/领地，后者为作者的历史解释。",
            "original_quotes": [
                {"source_span": "line 6", "text": "situated well within papal territory"},
                {"source_span": "line 43", "text": "the papal states were more and more affected by the general collapse of the Italian economy"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
                "source_span": "lines 3–11, 38–46; print pp. 146, 149",
            },
        },
        {
            "citation": BOOK,
            "location": "第6章；印刷页162；OCR L17",
            "sentence_summary": "Haskell 引述一位未具名威尼斯使节称教皇国贫困；这是归属明确的引语，不据此建立使节与国家之间的关系边。",
            "original_quotes": [{"source_span": "line 17", "text": "The States of the Church are very impoverished"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/06_CHP-6_sec_v.md",
                "source_span": "lines 14–19; print p. 162",
            },
        },
        {
            "citation": BOOK,
            "location": "第8章；印刷页203；OCR L8",
            "sentence_summary": "Haskell 将 Bologna 描述为教皇国境内的“second capital”；此为作者的历史表述，不推演现代或持续不变的行政地位。",
            "original_quotes": [{"source_span": "line 8", "text": "within the papal states themselves Bologna"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                "source_span": "lines 3–12; print p. 203 (S2 records OCR punctuation correction)",
            },
        },
        {
            "source_id": TRECCANI_ID,
            "citation": TRECCANI_CITATION,
            "location": "Opening definition",
            "sentence_summary": "Treccani identifies the State of the Church as a polity governed by the pope in his temporal capacity until 1870; used only to support S3 identity and institution type.",
            "original_quotes": [{"source_span": "opening definition", "text": "Lo Stato della Chiesa, governato dal papa fino al 1870."}],
        },
    ]
    fm = yaml.safe_dump(
        {
            "title": f"{ITEM['name_zh']}（{ITEM['name_en']}）",
            "name_en": ITEM["name_en"],
            "type": "institution",
            "evidence_status": "source_backed",
            "sources": sources,
            "created": "2026-10-17",
            "updated": "2026-10-17",
            "process_ref": f"03-processing/{TASK}/process/knowledge.md",
        },
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )
    p31 = "[第2章 p.31](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md)（L3–8）"
    p32 = "[第2章 p.32](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md)（L10–18）"
    p35 = "[第2章 p.35](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md)（L42–50）"
    p146 = "[第6章 p.146](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)（L3–11）"
    p149 = "[第6章 p.149](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)（L38–46）"
    p162 = "[第6章 p.162](../../../02-sources/02-Markdown/06_CHP-6_sec_v.md)（L14–19）"
    p203 = "[第8章 p.203](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md)（L3–12）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录 Haskell 称为 “Papal States” 或 “States of the Church” 的政治地域。第2章讨论其统治与财富，第6章称 Castro 位于 papal territory 并叙述其经济状况，第8章将 Bologna 描写为其中的第二首府。Treccani 将 Stato della Chiesa 界定为由教宗行使世俗统治的国家实体，并称其由教宗治理至1870年；该项只用于支持 S3 的身份与 institution 类型，不代替对 Haskell 具体说法的核验。{p31}；{p32}；{p146}；{p149}；{p162}；{p203}

**English:** This card records the polity Haskell calls the “Papal States” or “States of the Church.” Chapter 2 discusses its rule and wealth; Chapter 6 places Castro within papal territory and describes its economic condition; Chapter 8 calls Bologna a second capital within it. Treccani defines the State of the Church as a polity under the pope’s temporal rule and says it was governed by the pope until 1870; that source supports the S3 identity and institution type only, not Haskell’s specific historical claims. {p31}; {p32}; {p146}; {p149}; {p162}; {p203}

### 名称与身份边界

- S3 将 `cand-1831`、`cand-1832`、`cand-1833` 合为 `{GROUP}`：分别为主项、索引子项“increasing poverty”和“wealth of in 1623”。索引子项只定位同一政治实体，不另建术语 KU。
- 本卡表示政治地域/国家实体，与 Rome 城市及候选 `cand-4424` 所指 Holy See 分开；不把历史领土边界或政体结构推定为跨时期不变。
- 书内的 “Papal States”“States of the Church” 与相应 papal territory 表述在 S3 中归为同一实体；Treccani 仅辅助身份/类型判断，不证明书内每项历史陈述。

### 关系与证据

以下8条关系候选留待 S6；本卡未新增正式关系：

- `st-chp2-sec-ii-l10-18-urban-professed-wealth-policy`、`st-chp2-sec-ii-l10-18-urban-role-absolute-monarch`、`st-chp2-sec-ii-l3-8-sovereignty`：Haskell 对 Urban VIII 统治权与公开意图的不同表述，保留来源限定。
- `st-chp2-sec-ii-l10-18-venetian-income-estimate`、`st-chp2-secii-l42-50-cost_reported`：威尼斯使节收入估值及华盖造价/收入比较，均为书中转述或作者报告，未独立核实。
- `st-chp6-p146-castro-papal-territory`：Castro 位于教皇领地的地理表述；该城另有其所属公爵领地限定。
- `st-chp6-p149-italian-economic-collapse`：Haskell 对意大利经济衰退与教皇国受影响的解释。
- `st-chp8-p203-bologna-second-capital`：Bologna 被称为“second capital”的书内历史表述，不据此推定具体行政制度。

`st-chp2-sec-ii-l10-18-papal-states-wealth-at-accession` 的“rich enough”是相对评价；`st-chp6-p162-v1-05` 是未具名威尼斯使节的贫困评价引语。这两项在 S2 中均为非关系陈述，保留为来源主张，不升格为关系边。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Papal States cross-chapter institution group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    source_fields, sources = read_csv(SOURCES_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_rows = [candidate_by_id[candidate_id] for candidate_id in CANDIDATES]
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert all(row["canonical_name"] == "Papal states" and row["suggested_type"] == "institution" for row in candidate_rows)
    assert all(alignment_by_id[candidate_id]["decision"] == "new" and not alignment_by_id[candidate_id].get("ku_id") for candidate_id in CANDIDATES)
    assert all(sync.get_group(alignment_by_id[candidate_id].get("resolution_note", "")) == GROUP for candidate_id in CANDIDATES)
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert not CARD_PATH.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(row.get("type") == "institution" and row.get("name_en", "").casefold() == "papal states" for row in manifest)
    assert not any(row.get("url") == TRECCANI_URL or row.get("source_id") == TRECCANI_ID for row in sources)

    statements = [
        json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if any(candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id")) for candidate_id in CANDIDATES)
    ]
    assert {row["statement_id"] for row in direct} == RELATION_STATEMENTS | NON_RELATION_STATEMENTS
    relation_ids = {
        row["statement_id"] for row in direct
        if row.get("qualifiers", {}).get("relation_candidate") is True
    }
    assert relation_ids == RELATION_STATEMENTS

    chapter2a = (ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md").read_text(encoding="utf-8-sig")
    chapter2b = (ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md").read_text(encoding="utf-8-sig")
    chapter6a = (ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_i.md").read_text(encoding="utf-8-sig")
    chapter6v = (ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_v.md").read_text(encoding="utf-8-sig")
    chapter8 = (ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_i.md").read_text(encoding="utf-8-sig")
    assert "the supreme power in the state" in chapter2a
    assert "the papal states were rich enough" in chapter2b
    assert "two million scudi a year" in chapter2b
    assert "papal territory" in chapter6a and "the papal states were more and more affected" in chapter6a
    assert "The States of the Church are very impoverished" in chapter6v
    assert "within the papal states themselves Bologna" in chapter8

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for candidate_id in CANDIDATES:
        planned_by_id[candidate_id]["ku_id"] = KU_ID
        planned_by_id[candidate_id]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_by_id[CANDIDATES[0]]["resolution_note"] += (
        f" S3 source trace 2026-10-17: {TRECCANI_CITATION} source_id={TRECCANI_ID}; "
        "the opening definition supports historical polity identity and institution type only."
    )
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": ITEM["type"],
        "canonical_name": ITEM["name_zh"],
        "name_en": ITEM["name_en"],
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    planned_sources = list(sources)
    planned_sources.append({
        "source_id": TRECCANI_ID,
        "kind": "external",
        "label": TRECCANI_CITATION,
        "version": "",
        "accessed_date": "2026-10-17",
        "citation": TRECCANI_CITATION,
        "url": TRECCANI_URL,
    })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    audit_old = (
        "审计警告中的4,592条待登记 `decision=new` alignment 行，含4,577条候选决定映射（4,498组）和15条外部身份记录。"
    )
    audit_new = (
        "审计警告中的4,589条待登记 `decision=new` alignment 行，含4,574条候选决定映射（4,497组）和15条外部身份记录。"
    )
    assert audit_old in result_text
    result_text = result_text.replace(audit_old, audit_new, 1)
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S3 来源定位补录：Papal States 身份依据（2026-10-17）\n\n"
        f"`{GROUP}` 的既有 S3 理由提到 Treccani《Pontificio, Stato》，现将其完整记录补入 `sources.csv`："
        f"`{TRECCANI_ID}`，访问日期 2026-10-17，URL `{TRECCANI_URL}`。复核页面开篇定义确认其将 Stato della Chiesa 说明为教宗行使世俗统治的国家实体，并称治理延续至1870年。"
        "该来源只支持 S3 的政治实体身份与 `institution` 类型，不验证 Haskell 的具体收入、边界、主权或艺术史陈述。"
    )
    process_text += (
        "\n\n### S4 institution：Papal States 跨章身份组登记（2026-10-17）\n\n"
        f"`cand-1831`（P.csv#30）、`cand-1832`（P.csv#31）与 `cand-1833`（P.csv#32）保持 S3 组 `{GROUP}`，"
        f"登记为[教皇国机构卡](../../../04-knowledge/units/institutions/papal-states.md)；三条候选映射至一个 KU。"
        "第2、6、8章语境与名称锚点支持同一政治地域；Rome 城市及 Holy See 候选 `cand-4424` 保持分开。"
        "8条直接关系候选留待 S6；两条关于财富的 statement 是非关系陈述。Treccani 来源仅补足身份/类型追溯，本轮未做 S5、未写正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
        f"sources.csv 新增1条外部身份来源（{TRECCANI_ID}）。"
    )
    result_text += (
        "\n\n### S4 institution：Papal States 跨章身份组（2026-10-17）\n\n"
        f"`cand-1831`、`cand-1832`、`cand-1833` 共映射至[教皇国卡](../units/institutions/papal-states.md)。"
        "书内名称及第2、6、8章地域语境支持同一政治实体；Treccani 仅支持身份/类型，不扩展书中具体史实。"
        "8条关系候选留待 S6，两个非关系陈述仍按原分类保留。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    if args.dry_run:
        print(f"S4 Papal States dry-run passed: {', '.join(CANDIDATES)} -> {KU_ID}")
        print("cross-chapter type boundary: institution; separate from Rome city and Holy See candidate cand-4424")
        print(f"direct statements={len(direct)}; relation candidates={len(relation_ids)}; non-relations={len(NON_RELATION_STATEMENTS)}")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; sources={len(sources):,}->{len(planned_sources):,}")
        print(
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("source excerpts, Treccani identity/type scope, group membership, and unique destination checked; no files changed")
        return 0

    CARD_PATH.write_text(card_text(), encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    write_csv(SOURCES_PATH, source_fields, planned_sources)
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
        f"applied: {', '.join(CANDIDATES)} -> {KU_ID}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}; sources={sync.fmt(len(planned_sources))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
