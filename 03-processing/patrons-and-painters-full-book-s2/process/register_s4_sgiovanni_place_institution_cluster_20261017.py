from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-s-giovanni-decollato-place-institution"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

CH5 = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
CH6 = "02-sources/02-Markdown/06_CHP-6_sec_i.md"


def source(location: str, summary: str, quotes: list[tuple[str, str]], file: str, span: str) -> dict:
    return {
        "citation": BOOK_CITATION,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [
            {"source_span": source_span, "text": quote}
            for source_span, quote in quotes
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": file,
            "source_span": span,
        },
    }


TARGETS = [
    {
        "candidate": "cand-6040",
        "group": "sg3-place-cand-6040",
        "ku": "units/places/s-giovanni-decollato-church-rome",
        "type": "place",
        "name_zh": "圣若望斩首堂（罗马）",
        "name_en": "Church of S. Giovanni Decollato, Rome",
        "sources": [
            source(
                "第5章第I节；印刷页127；OCR L78–81",
                "Haskell places the annual exhibition in the cloisters of S. Giovanni Decollato and says that the pictures were almost certainly intended to decorate the church for the saint's celebration. The OCR spelling is Decollate; the S2 visual comparison records Decollato on the printed page.",
                [
                    ("lines 78–79", "The other great annual exhibition held in Rome took place in the cloisters of S.\nGiovanni Decollate on 29 August, the saint’s day."),
                    ("line 80", "Almost certainly the pictures were designed to decorate the church as part of the celebrations in honour of the saint."),
                ],
                CH5,
                "lines 78–81; print p. 127",
            ),
            source(
                "第5章第I节；印刷页128；OCR L88",
                "Haskell says that in the 1675 display works were shown inside the cloisters and in a room opening onto them.",
                [("line 88", "inside the cloisters and in one of the rooms opening on to them were works by living and dead artists including Raphael, Titian and the Carracci.")],
                CH5,
                "line 88; print p. 128",
            ),
            source(
                "第6章第I节；印刷页154；OCR L93",
                "Haskell says Salvator Rosa exhibited a picture at S. Giovanni Decollato; this venue reference supplies no date.",
                [("line 93", "Rosa exhibited it at S. Giovanni Decollato.")],
                CH6,
                "line 93; print p. 154",
            ),
        ],
        "body": """## 内容

### 描述

**中文：** 本卡记录哈斯克尔在第5、6章所指的罗马 S. Giovanni Decollato 教堂。第5章把年度展览置于该堂回廊，并称画作几乎可以肯定用于圣人庆典中的教堂装饰；1675年的叙述又区分回廊与一间通向回廊的房间。第6章另称 Salvator Rosa 曾在 S. Giovanni Decollato 展出一幅画，但该句没有给出日期。教堂建筑与[回廊](s-giovanni-decollato-cloisters-rome.md)、[年度展览系列](../events/annual-exhibition-s-giovanni-decollato.md)及有日期的展览场次分别建模。中文显示名为工作译名；书内 OCR 行保留 “Decollate”，S2 对照印刷页将名称判读为 “Decollato”，未改写 S0 来源文本。〔[第5章 p.127](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L78–81）；[第5章 p.128](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L88）；[第6章 p.154](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)（L93）〕

**English:** This unit records the Roman church of S. Giovanni Decollato as referred to by Haskell in Chapters 5 and 6. Chapter 5 places the annual exhibition in its cloisters and says the pictures were almost certainly intended to decorate the church for the saint's celebration; the account of 1675 distinguishes the cloisters from a room opening onto them. Chapter 6 separately says that Salvator Rosa exhibited a picture at S. Giovanni Decollato, without giving a date in that sentence. The church building is modeled separately from the [cloisters](s-giovanni-decollato-cloisters-rome.md), the [annual exhibition series](../events/annual-exhibition-s-giovanni-decollato.md), and dated occurrences. The Chinese display name is a working translation. The source OCR retains “Decollate”; S2's comparison with the printed page reads “Decollato,” while the S0 source text remains unchanged. ([Chapter 5, p. 127](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md) (lines 78–81); [Chapter 5, p. 128](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md) (line 88); [Chapter 6, p. 154](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md) (line 93).)

### 名称与对象边界

- 书中名称：S. Giovanni Decollato；p.127 OCR 转录为 Decollate，S2 的印刷页对照记录为 Decollato。
- 对象类型：罗马教堂地点。此卡只记录书内指称，不补写建筑沿革或外部身份标识。
- 空间边界：教堂建筑与内部回廊分别记录；p.128 所述通向回廊的房间不在本卡中另建身份。
- 展览边界：年度系列及 1668、1675 年场次均保留为独立事件知识元；第6章的 Rosa 展出地点未据此补定日期。

## 关系与证据

当前没有登记为 S6 正式关系的记录。教堂端点对应的直接 S2 关系候选仍留待 S6 审查。""",
    },
    {
        "candidate": "cand-6041",
        "group": "sg3-place-cand-6041",
        "ku": "units/places/s-giovanni-decollato-cloisters-rome",
        "type": "place",
        "name_zh": "圣若望斩首堂回廊（罗马）",
        "name_en": "Cloisters of S. Giovanni Decollato, Rome",
        "sources": [
            source(
                "第5章第I节；印刷页127；OCR L78",
                "Haskell identifies the cloisters as the venue for the annual exhibition on 29 August.",
                [("line 78", "The other great annual exhibition held in Rome took place in the cloisters of S.\nGiovanni Decollate on 29 August, the saint’s day.")],
                CH5,
                "lines 78–79; print p. 127",
            ),
            source(
                "第5章第I节；印刷页128；OCR L88",
                "For the 1675 occurrence, Haskell distinguishes works displayed in the cloisters from works in a room opening onto them.",
                [("line 88", "inside the cloisters and in one of the rooms opening on to them were works by living and dead artists including Raphael, Titian and the Carracci.")],
                CH5,
                "line 88; print p. 128",
            ),
        ],
        "body": """## 内容

### 描述

**中文：** 本卡记录哈斯克尔所述罗马 S. Giovanni Decollato 教堂内部的回廊。第5章将年度展览的场所明确称为该堂回廊；在1675年场次的叙述中，作者又把回廊与一间通向回廊的房间区分开。回廊作为内部空间，与[教堂建筑](s-giovanni-decollato-church-rome.md)、[年度展览系列](../events/annual-exhibition-s-giovanni-decollato.md)和具体届次分别建模。书中 OCR 写作 “Decollate”；S2 对照印刷页判读为 “Decollato”，原 OCR 来源保持不变。〔[第5章 p.127](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L78–79）；[第5章 p.128](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L88）〕

**English:** This unit records the cloisters inside the church of S. Giovanni Decollato in Rome as described by Haskell. Chapter 5 explicitly locates the annual exhibition in the cloisters; in the account of the 1675 occurrence, the author distinguishes the cloisters from a room opening onto them. The cloisters are modeled as an interior space, separately from the [church building](s-giovanni-decollato-church-rome.md), the [annual exhibition series](../events/annual-exhibition-s-giovanni-decollato.md), and individual occurrences. The source OCR reads “Decollate”; S2's comparison with the printed page reads “Decollato,” and the OCR source remains unchanged. ([Chapter 5, p. 127](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md) (lines 78–79); [Chapter 5, p. 128](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md) (line 88).)

### 名称与对象边界

- 书中空间称谓：the cloisters of S. Giovanni Decollato；中文名为描述性工作译名。
- 对象类型：教堂内部回廊地点；不与教堂建筑合并。
- 其他空间：p.128 所述通向回廊的房间是另一个空间指称，本卡不将其并入回廊，也不另建未命名房间知识元。

## 关系与证据

当前没有登记为 S6 正式关系的记录。回廊对应的直接 S2 关系候选仍留待 S6 审查。""",
    },
    {
        "candidate": "cand-6048",
        "group": "sg3-institution-cand-6048",
        "ku": "units/institutions/compagnia-della-misericordia-s-giovanni-decollato",
        "type": "institution",
        "name_zh": "圣若望斩首堂语境中的慈悲会",
        "name_en": "Compagnia della Misericordia (S. Giovanni Decollato context)",
        "sources": [
            source(
                "第5章第I节；印刷页127；OCR L81",
                "Haskell says that Camillo Rospigliosi and his four sons had just been admitted as novices to the Compagnia della Misericordia, which administered the church.",
                [("line 81", "he and his four sons had just been admitted as novices to the Compagnia della Misericordia which administered the church.")],
                CH5,
                "line 81; print p. 127",
            )
        ],
        "body": """## 内容

### 描述

**中文：** 本卡记录哈斯克尔在第5章称为 Compagnia della Misericordia 的机构。第5章说，1668年负责组织展览的 Camillo Rospigliosi 与其四名儿子刚被接纳为该会的 novices，并称该会管理 S. Giovanni Decollato 教堂。此处只登记书内可辨认的组织及其与教堂的管理关系；不推定 Rospigliosi 家族成员因此担任其他职务，也不将它与其他同名机构合并。中文显示名是依原名制作的描述性工作译名，意大利语名称保留。〔[第5章 p.127](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L81）〕

**English:** This unit records the organization that Haskell calls the Compagnia della Misericordia in Chapter 5. The passage says that Camillo Rospigliosi, who organized the 1668 exhibition, and his four sons had just been admitted as novices to the Compagnia, which administered the church of S. Giovanni Decollato. This unit records only the source-identifiable organization and its stated administrative connection to the church; it does not infer other offices for the Rospigliosi family or merge this group with other similarly named organizations. The Chinese display name is a descriptive working translation; the Italian name is retained. ([Chapter 5, p. 127](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md) (line 81).)

### 名称与基本信息

- 原文名称：Compagnia della Misericordia。
- 中文显示名：圣若望斩首堂语境中的慈悲会；描述性工作译名，不宣称为正式中文名称。
- 书中机构性质：管理 S. Giovanni Decollato 教堂的组织；Haskell 称 Rospigliosi 父子为该会新近接纳的 novices。
- 身份范围：按本书在圣若望斩首堂语境中的称谓登记；外部机构身份及与其他同名团体的关系未在此确认。

## 关系与证据

当前没有登记为 S6 正式关系的记录。该机构端点对应的直接 S2 关系候选仍留待 S6 审查。""",
    },
]

EXPECTED_RELATIONS = {
    "cand-6040": {
        "st-chp5-p127-exhibition-church-decoration-purpose",
        "st-chp5-p127-misericordia-administered-church",
        "st-chp5-p127-rospigliosi-display-spaces",
        "st-chp5-p128-medici-outdoor-stage-setting",
        "st-chp5-p128-medici-textiles-displayed",
        "st-chp6-p154-rosa-exhibits-picture-at-s-giovanni",
    },
    "cand-6041": {
        "st-chp5-p127-san-giovanni-exhibition-setting",
        "st-chp5-p128-medici-interior-display",
    },
    "cand-6048": {
        "st-chp5-p127-misericordia-administered-church",
        "st-chp5-p127-rospigliosi-sons-novices",
        "st-chp5-p127-sons-novices",
    },
}


def make_card(target: dict) -> str:
    frontmatter = {
        "title": f"{target['name_zh']}（{target['name_en']}）",
        "name_en": target["name_en"],
        "type": target["type"],
        "evidence_status": "source_backed",
        "sources": target["sources"],
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{fm}---\n\n{target['body'].strip()}\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the S. Giovanni Decollato place and institution S3 groups in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = sync.read_csv(ENTITY_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert len({item["candidate"] for item in TARGETS}) == len(TARGETS)
    assert len({item["group"] for item in TARGETS}) == len(TARGETS)
    assert len({item["ku"] for item in TARGETS}) == len(TARGETS)
    manifest_ids = {row["ku_id"] for row in manifest}
    manifest_paths = {row["card_path"] for row in manifest}
    accepted_paths = set(accepted.splitlines())

    for item in TARGETS:
        cid = item["candidate"]
        assert cid in candidate_by_id and candidate_by_id[cid]["suggested_type"] == item["type"]
        assert cid in alignment_by_id
        alignment = alignment_by_id[cid]
        assert alignment["decision"] == "new" and not alignment.get("ku_id"), cid
        assert sync.get_group(alignment.get("resolution_note", "")) == item["group"], cid
        group_rows = [
            row for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == item["group"]
        ]
        assert [row["candidate_id"] for row in group_rows] == [cid], (item["group"], group_rows)
        card_rel = f"04-knowledge/{item['ku']}.md"
        assert item["ku"] not in manifest_ids and card_rel not in manifest_paths
        assert not (ROOT / card_rel).exists()
        assert f"- {card_rel}" not in accepted_paths

    statements = sync.load_statements()
    for cid, expected in EXPECTED_RELATIONS.items():
        direct = {
            row["statement_id"] for row in statements
            if (row.get("subject_candidate_id") == cid or row.get("object_candidate_id") == cid)
            and (row.get("qualifiers") or {}).get("relation_candidate") is True
        }
        assert direct == expected, (cid, direct ^ expected)

    for item in TARGETS:
        for source_item in item["sources"]:
            source_path = ROOT / source_item["evidence_ref"]["source_file"]
            source_text = " ".join(source_path.read_text(encoding="utf-8-sig").split())
            for quote in source_item["original_quotes"]:
                assert " ".join(quote["text"].split()) in source_text, (source_path, quote["text"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_manifest = list(manifest)
    for item in TARGETS:
        target_alignment = planned_by_id[item["candidate"]]
        target_alignment["ku_id"] = item["ku"]
        target_alignment["resolution_note"] += f" S4 registration: mapped {item['group']} to {item['ku']}."
        planned_manifest.append({
            "ku_id": item["ku"],
            "type": item["type"],
            "canonical_name": item["name_zh"],
            "name_en": item["name_en"],
            "source_task": TASK,
            "card_path": f"04-knowledge/{item['ku']}.md",
        })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(section[key] for section in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    relation_total = sum(len(ids) for ids in EXPECTED_RELATIONS.values()) - 1
    process_text += (
        "\n\n<a id=\"s4-s-giovanni-decollato-place-institution\"></a>\n\n"
        "### S4 place／institution：圣若望斩首堂跨章场所与管理机构登记（2026-10-17）\n\n"
        "`cand-6040`（`sg3-place-cand-6040`）登记为[罗马圣若望斩首堂地点](../../../04-knowledge/units/places/s-giovanni-decollato-church-rome.md)；"
        "`cand-6041`（`sg3-place-cand-6041`）登记为该堂内部[回廊地点](../../../04-knowledge/units/places/s-giovanni-decollato-cloisters-rome.md)；"
        "`cand-6048`（`sg3-institution-cand-6048`）登记为本书语境中的[Compagnia della Misericordia 机构](../../../04-knowledge/units/institutions/compagnia-della-misericordia-s-giovanni-decollato.md)。"
        "S3 的三个新组分别保持 place、place、institution 类型；没有与既有年度展览系列及1668、1675场次合并。第5章 p.127–128 记载教堂、回廊和管理机构，第6章 p.154 再次提及 Rosa 在 S. Giovanni Decollato 展画，构成地点的跨章来源锚点。"
        "第5章 OCR 的 Decollate 沿用原文转录；S2 既有印刷页核对记录为 Decollato，本次没有改写 S0。"
        f"教堂、回廊及机构端点对应{relation_total}条不同的直接 relation_candidate，仍留待 S6；未写入 relations.csv 或新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 place／institution：圣若望斩首堂与回廊跨章端点登记（2026-10-17）\n\n"
        "`cand-6040`、`cand-6041`、`cand-6048` 分别登记为[教堂地点](../units/places/s-giovanni-decollato-church-rome.md)、"
        "[内部回廊地点](../units/places/s-giovanni-decollato-cloisters-rome.md)和[Compagnia della Misericordia 机构](../units/institutions/compagnia-della-misericordia-s-giovanni-decollato.md)。"
        "第5章展览及空间叙述与第6章 Rosa 的场地提及支持地点跨章归组；OCR 与印刷页拼写差异保留可追溯说明。"
        f"{relation_total}条不同的直接关系候选待 S6；未新增正式关系。S4 登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    accepted_lines = accepted.splitlines()
    for item in TARGETS:
        card_rel = f"04-knowledge/{item['ku']}.md"
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {card_rel}")
    planned_accepted = "\n".join(accepted_lines) + "\n"
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    if args.dry_run:
        print(f"S4 place/institution dry-run passed: groups={len(TARGETS)}; direct relation candidates={relation_total}")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; accepted paths added={len(TARGETS)}")
        print(
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("candidate groups, type boundaries, source quotations, and relation-candidate endpoints checked; no files changed")
        return 0

    for item in TARGETS:
        card_path = ROOT / "04-knowledge" / f"{item['ku']}.md"
        card_path.write_text(make_card(item), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups={len(TARGETS)}; registered={sync.fmt(totals['registered_groups'])}/"
        f"{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/"
        f"{sync.fmt(totals['pending_members'])}; manifest={len(planned_manifest):,}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
