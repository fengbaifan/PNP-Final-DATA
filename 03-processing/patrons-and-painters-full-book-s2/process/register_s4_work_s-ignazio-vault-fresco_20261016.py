from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import fitz
import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as result_sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"

CANDIDATE = "cand-5074"
GROUP = "workgrp-1c890e82018f20"
KU_ID = "units/works/pozzo-fresco-vault-s-ignazio"
CARD_REL = "04-knowledge/units/works/pozzo-fresco-vault-s-ignazio.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "圣依纳爵堂拱顶壁画"
NAME_EN = "Fresco on the Vault of S. Ignazio"
MODEL_KU = "units/works/andrea-pozzo-modello-for-fresco-on-vault-of-s-ignazio"
MODEL_CANDIDATE = "cand-4002"
DOME_CANDIDATE = "cand-5368"
OCR_STATEMENT_IDS = (
    "st-chp3-seciv-l141-150-pozzo-described-ray-from-jesus-through-ignatius",
    "st-chp3-seciv-l141-150-fresco-depicts-ignatius-transmitting-ray",
)
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = (
    {
        "location": "章前图版目录；印刷页xii；OCR L63–64",
        "summary": "图版15题注把 Andrea Pozzo 的 modello 说明为 S. Ignazio 拱顶壁画的模型；该模型是壁画的不同对象。",
        "quotes": (
            ("lines 63–64", "15 Andrea Pozzo: Modello for fresco on vault of S. Ignazio, Rome"),
        ),
        "checks": (("lines 63–64", "15 Andrea Pozzo: Modello for fresco on vault of S. Ignazio, Rome"),),
        "span": "lines 63–64; front matter plate list; print p. xii",
        "source_file": "02-sources/02-Markdown/00_05_List_of_Plates.md",
    },
    {
        "location": "第3章；印刷页90；OCR L147",
        "summary": "Haskell转引画家传记称，Pozzo较早的穹顶绘画声誉促成了在同一教堂整面拱顶作画的想法；耶稣会一度考虑放弃，后于1688年由 Pozzo 开始该工程。",
        "quotes": (
            ("lines 147", "the extraordinary reputation acquired through this painting [the dome], not only by Padre Andrea, the artist, but also by the Society, which commissioned it, that the idea was born of painting the entire vault of the same church of S. Ignazio"),
            ("lines 147", "They considered, therefore, abandoning the work and leaving the vault as it was. But by now it was too late, and in 1688 Pozzo began his colossal undertaking (Plate 15)."),
        ),
        "checks": (),
        "span": "lines 147; print p. 90",
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
    },
    {
        "location": "第3章；印刷页90；OCR L148–150；PDF物理页32",
        "summary": "Haskell称 Pozzo 后来解释其壁画含义，并转引其自述：耶稣向依纳爵之心发出光线，再由圣人传向远方；另一光线照向带有耶稣圣名的盾牌。OCR 将 light 误识为 fight，扫描印刷页读作 light。",
        "quotes": (
            ("lines 148", "In later years the artist himself explained the meaning of his fresco at great length."),
            ("lines 150", "I have painted the figure of Jesus, who sends forth a ray of light to the heart of Ignatius, which is then transmitted by him to the most distant hearts of the four parts of the world."),
            ("lines 150", "From the breast of the Redeemer there emerges another ray which strikes a shield, on which is painted the Name of Jesus, the crown of light."),
        ),
        "checks": (
            ("lines 150", "I have painted the figure of Jesus, who sends forth a ray of fight to the heart of Ignatius, which is then transmitted by him to the most distant hearts of the four parts of the world."),
            ("lines 150", "From the breast of the Redeemer there emerges another ray which strikes a shield, on which is painted the Name of Jesus, the crown of light."),
        ),
        "span": "lines 148–150; print p. 90; PDF physical p. 32",
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
    },
)


def make_card():
    source_rows = []
    for item in SOURCES:
        source_rows.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [
                {"source_span": span, "text": quote}
                for span, quote in item["quotes"]
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["source_file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "work",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p90 = "[第3章 p.90](../../../02-sources/02-Markdown/03_CHP-3_sec_iv.md)（L147–150）"
    scan = "[第3章扫描页](../../../02-sources/01-book/CHP-3.pdf)（PDF物理页32；印刷页90）"
    caption = "[图版目录 p. xii](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)（L63–64）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录罗马 S. Ignazio（圣依纳爵堂）拱顶的壁画作品。第3章图版15题注将 Pozzo 的 modello 标为该壁画的模型；正文称 Pozzo 于1688年开始整面拱顶的绘画工程，并转引他后来对壁画图像含义的解释。此处题名为描述性工作译名；图版模型及同堂较早的穹顶绘画另属不同作品。{caption} {p90}

**English:** This unit records the fresco on the vault of S. Ignazio in Rome. The Chapter 3 caption to Plate 15 identifies Pozzo’s modello as a model for this fresco; the text says Pozzo began the project to paint the entire vault in 1688 and quotes his later explanation of the fresco’s iconography. The title is descriptive; the plate modello and the earlier dome painting in the same church are separate works. {caption} {p90}

### 作品边界与创作过程

- 作品性质：S. Ignazio 拱顶的壁画；图版15的 modello 是另一件作品，见[拱顶壁画模型卡](../works/andrea-pozzo-modello-for-fresco-on-vault-of-s-ignazio.md)。模型题注明确其预备稿性质，不与完成壁画合并。{caption}
- 较早的穹顶绘画：Haskell 转引画家传记称，该绘画的声誉促成了在同一教堂绘制整个拱顶的构想；前一穹顶作品与本壁画分属不同作品。{p90}
- 创作开始：1688年 Pozzo 开始整面拱顶壁画工程。该段未给出完成年份。{p90} {scan}
- 工程阻碍：壁画之前拱顶曾装饰灰泥；拆除后遭到攻击，耶稣会一度考虑放弃工程，Haskell称当时已经为时过晚。{p90}
- 图像说明：Haskell 转引 Pozzo 后来的解释，称耶稣向依纳爵之心发出光线，并由依纳爵传向远方；另一光线射向绘有耶稣圣名的盾牌。该引文来自 Haskell 对 Pozzo 文字的转引，本轮未独立查阅所引原始文本。扫描印刷页读作 *light*；OCR 原文误识为 *fight*。{p90} {scan}
- 地点：罗马 S. Ignazio（圣依纳爵堂）地点实体另见[地点卡](../places/s-ignazio.md)。{caption} {p90}

## 关系与证据

### 关系记录

当前没有已登记的正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def load_and_correct_statements():
    raw_lines = STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
    updated_lines = []
    found = set()
    for line in raw_lines:
        if not line.strip():
            updated_lines.append(line)
            continue
        row = json.loads(line)
        if row.get("statement_id") in OCR_STATEMENT_IDS:
            found.add(row["statement_id"])
            qualifiers = row.setdefault("qualifiers", {})
            correction = {
                "source_line": 150,
                "ocr": "fight",
                "print": "light",
                "basis": "CHP-3.pdf physical page 32; printed p. 90 scan",
            }
            corrections = qualifiers.setdefault("ocr_corrections", [])
            if correction not in corrections:
                corrections.append(correction)
            note = "The scan of printed p. 90 reads ‘light’; the S0 OCR reads ‘fight’."
            current_qualification = qualifiers.get("qualification", "")
            already_documented = "reads ‘light’" in current_qualification and "reads ‘fight’" in current_qualification
            if note not in current_qualification and not already_documented:
                qualifiers["qualification"] = (current_qualification.rstrip() + " " + note).strip()
            line = json.dumps(row, ensure_ascii=False)
        updated_lines.append(line)
    assert found == set(OCR_STATEMENT_IDS), f"unexpected OCR correction targets: {found}"
    return raw_lines, updated_lines


def main():
    parser = argparse.ArgumentParser(description="Register Pozzo's S. Ignazio vault fresco in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert CANDIDATE in candidate_by_id and candidate_by_id[CANDIDATE].get("suggested_type") == "work"
    target = decisions[CANDIDATE]
    assert target["decision"] == "new" and not target.get("ku_id")
    assert result_sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and result_sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert CARD_REL not in accepted
    assert decisions[MODEL_CANDIDATE]["decision"] == "same" and decisions[MODEL_CANDIDATE]["ku_id"] == MODEL_KU
    assert decisions[DOME_CANDIDATE]["decision"] == "new" and not decisions[DOME_CANDIDATE].get("ku_id")
    assert decisions["cand-3967"]["decision"] == "same" and decisions["cand-3967"]["ku_id"] == "units/places/s-ignazio"
    assert any(row.get("ku_id") == MODEL_KU for row in manifest)

    for item in SOURCES:
        source = ROOT / item["source_file"]
        source_text = " ".join(source.read_text(encoding="utf-8-sig").split())
        for span, quote in item.get("checks", ()) or item["quotes"]:
            assert " ".join(quote.split()) in source_text, (item["location"], span, quote)
    pdf = fitz.open(ROOT / "02-sources/01-book/CHP-3.pdf")
    try:
        scan_p90 = pdf[31].get_text()
        assert re.search(r"\b90\b", scan_p90[:80]), "selected PDF page is not printed p.90"
        assert "ray of fight" in scan_p90, "expected OCR-layer misread not found"
    finally:
        pdf.close()

    statements = result_sync.load_statements()
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    direct_relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate")]
    assert len(direct) == 14 and len(direct_relations) == 14
    old_statement_lines, corrected_statement_lines = load_and_correct_statements()

    planned_alignment = [dict(row) for row in alignments]
    mapped = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    mapped["ku_id"] = KU_ID
    mapped["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "work",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    stats = result_sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = result_sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_note = (
        "\n\n### S2 OCR 校正与 S4 work：Pozzo 圣依纳爵堂拱顶壁画（2026-10-16）\n\n"
        f"`{CANDIDATE}`（`{GROUP}`）登记至[圣依纳爵堂拱顶壁画作品卡](../../../04-knowledge/units/works/pozzo-fresco-vault-s-ignazio.md)。"
        "组内身份为实际拱顶壁画：图版15模型 `cand-4002` 已 same 至既有模型稿卡；较早的 dome painting 候选 `cand-5368` 保持独立 new 组并待 S4；教堂候选 `cand-3967` same 至既有地点卡。"
        "第3章 p.90 记录1688年开工、此前考虑放弃、及 Haskell 转引 Pozzo 对图像的解释；未推定完工年。14条直接陈述均为 S2 关系候选，留待 S6。"
        "扫描 CHP-3.pdf 物理页32（印刷 p.90）读作 ray of light；源 OCR 误作 ray of fight。为保持原始 OCR 摘录可追溯，两个相关 S2 statement 保留 original_quote 原文并补入 `ocr_corrections` 与 scan qualification；其他 S2 判断不变。"
        "本轮未新增正式关系或开展 S5。"
        f"S4 累计登记{result_sync.fmt(totals['registered_groups'])}组/{result_sync.fmt(totals['registered_members'])}条映射，待登记{result_sync.fmt(totals['pending_groups'])}组/{result_sync.fmt(totals['pending_members'])}条。"
    )
    result_note = (
        "\n\n### work：圣依纳爵堂拱顶壁画 S4 登记（2026-10-16）\n\n"
        f"`{CANDIDATE}` 映射至[圣依纳爵堂拱顶壁画作品卡](../units/works/pozzo-fresco-vault-s-ignazio.md)。"
        "该壁画与图版15的模型稿、同堂较早的穹顶绘画分别保持独立身份；S2 两条引用中的 OCR ‘fight’ 已据印刷页扫描校正为 ‘light’，原始 OCR 摘录继续保留并附校正记录。"
        "原书称 Pozzo 于1688年开始拱顶绘画工程，未提供完工年。14条直接 S2 陈述均为关系候选，留待 S6；本轮未新增正式关系或开展 S5。"
        f"全书 S4 当前登记{result_sync.fmt(totals['registered_groups'])}组/{result_sync.fmt(totals['registered_members'])}条映射，待登记{result_sync.fmt(totals['pending_groups'])}组/{result_sync.fmt(totals['pending_members'])}条。"
    )
    process_text += process_note
    result_text += result_note

    if args.dry_run:
        print(f"S4 work dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"same model={MODEL_CANDIDATE} -> {MODEL_KU}; separate dome group={DOME_CANDIDATE}; direct statements={len(direct)}; relation candidates={len(direct_relations)}")
        print("Plate 15 and Chapter 3 p.90 quotations checked; scan confirms light over OCR fight")
        print(f"S2 OCR correction targets={len(OCR_STATEMENT_IDS)}; planned candidate mapping unique; no files changed")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; registered={result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['registered_members'])}; pending={result_sync.fmt(totals['pending_groups'])}/{result_sync.fmt(totals['pending_members'])}")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    result_sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    result_sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    STATEMENTS_PATH.write_text("\n".join(corrected_statement_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; OCR statements corrected={len(OCR_STATEMENT_IDS)}; "
        f"manifest={len(planned_manifest):,}; registered={result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['registered_members'])}; "
        f"pending={result_sync.fmt(totals['pending_groups'])}/{result_sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
