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
    "candidate": "cand-1487",
    "group": "new-person:maffei-scipione-5c81fca946",
    "ku_id": "units/persons/scipione-maffei",
    "card_rel": "04-knowledge/units/persons/scipione-maffei.md",
    "card_path": ROOT / "04-knowledge" / "units" / "persons" / "scipione-maffei.md",
    "type": "person",
    "name_zh": "斯基皮奥内·马费伊",
    "name_en": "Scipione Maffei",
}
TERM = {
    "candidate": "cand-12249",
    "group": "sg3-term-cand-12249",
    "ku_id": "units/terms/antique-sculpture-maffei-context",
    "card_rel": "04-knowledge/units/terms/antique-sculpture-maffei-context.md",
    "card_path": ROOT / "04-knowledge" / "units" / "terms" / "antique-sculpture-maffei-context.md",
    "type": "term",
    "name_zh": "古代雕塑（马费伊收藏语境）",
    "name_en": "Antique Sculpture (Maffei Collecting Context)",
}
PERSON_STATEMENTS = {
    "st-chp8-p230-ferdinand-supported-scipione-maffei",
    "st-chp10-p320-lodoli-in-touch-with-scipione-maffei",
    "st-chp15-p372-maffei-collected-antique-sculpture",
    "st-chp15-p372-querini-distinguished-from-maffei",
    "st-chp15-p372-maffei-recorded-evidence-of-the-past",
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


def source(location: str, summary: str, file: str, span: str, quote: str):
    return {
        "citation": BOOK,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span.split(";", 1)[0], "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/02-Markdown/{file}",
            "source_span": span,
        },
    }


def make_card(item: dict, description_zh: str, description_en: str, sources: list[dict], details: str) -> str:
    fm = yaml.safe_dump({
        "title": f"{item['name_zh']}（{item['name_en']}）",
        "name_en": item["name_en"],
        "type": item["type"],
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** {description_zh}

**English:** {description_en}

### 名称与语境

{details}

## 关系与证据

关系候选均留待 S6 按端点、方向、语境与证据逐条审查；本卡未新增正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def person_card() -> str:
    person_sources = [
        source(
            "第8章；印刷页230；OCR L229–230",
            "Haskell 将 Scipione Maffei 列为 Ferdinand 所支持的作家之一。",
            "08_CHP-8_sec_ii.md",
            "lines 229–230; print p. 230",
            "He supported writers such as Apostolo Zeno,\nBenedetto Menzini and Scipione Maffei",
        ),
        source(
            "第10章；印刷页320；OCR L162",
            "Haskell 称 Lodoli 在威尼斯以外与 Scipione Maffei 有联系，但未说明时间或联系媒介。",
            "10_CHP-10_sec_ii.md",
            "line 162; print p. 320",
            "Outside Venice he was in touch with Montesquieu and Scipione Maffei.",
        ),
        source(
            "第15章；印刷页372；OCR L87",
            "Haskell 将 Scipione Maffei 描述为较早一代的古代雕塑收藏者，并称其曾记录过去的遗存。",
            "15_CHP-15_sec_ii.md",
            "line 87; print p. 372",
            "Scipione Maffei who in an earlier generation had also collected antique sculpture and lovingly recorded the evidences of the past.",
        ),
    ]
    p8 = "[第8章 p.230](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)（L229–230）"
    p10 = "[第10章 p.320](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L162）"
    p15 = "[第15章 p.372](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)（L87）"
    return make_card(
        PERSON,
        f"本卡对应索引人物 Scipione Maffei（M.csv#24），第8、10、15章均以全名指称。Haskell 将他列为 Ferdinand 所支持的作家之一，称 Lodoli 在威尼斯以外与他有联系，并把他描述为较早一代的古代雕塑收藏者及过去遗存的记录者。有关描述均按原书语境保存；“lovingly”是作者评价，不转写为客观判断。{p8}；{p10}；{p15}",
        f"This card represents the indexed person Scipione Maffei (M.csv#24), named in full in Chapters 8, 10, and 15. Haskell lists him among writers supported by Ferdinand, says Lodoli was in touch with him outside Venice, and describes him as an earlier-generation collector of antique sculpture who recorded evidence of the past. These accounts remain source-bounded; “lovingly” is Haskell’s characterization, not recast as an objective judgment. {p8}; {p10}; {p15}",
        person_sources,
        f"索引形式为 “Maffei, Scipione”，页码定位为230、272、320；正文全名锚点见 p.230、p.320 与 p.372。索引只作定位，不单独充当身份事实。中文显示名为工作音译。\n\n第8章在 Ferdinand 的艺术赞助叙述中提到 Maffei；第10章在 Lodoli 威尼斯以外的交往名单中提到他；第15章比较 Angelo Querini 与 Maffei 对古代的不同态度。没有同名既有 person KU；本卡不补充外部身份、生卒或未经本书支持的履历。",
    )


def term_card() -> str:
    term_source = source(
        "第15章；印刷页372；OCR L87",
        "Haskell 在描述 Maffei 的收藏时提到古代雕塑；该类称谓不指某一雕塑、完整收藏或确定作品集。",
        "15_CHP-15_sec_ii.md",
        "line 87; print p. 372",
        "Scipione Maffei who in an earlier generation had also collected antique sculpture",
    )
    p15 = "[第15章 p.372](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)（L87）"
    return make_card(
        TERM,
        f"本卡登记原书在 Scipione Maffei 收藏语境中提到的“古代雕塑”这一通类。Haskell 仅称 Maffei 收藏过 antique sculpture，没有列出具体作品、构成或一套确定的雕塑收藏；本卡不把该通类扩展为具体对象清单。中文题名是说明语境的工作名称。{p15}",
        f"This card registers the generic category “antique sculpture” as it appears in Haskell’s account of Scipione Maffei’s collecting. Haskell says only that Maffei collected antique sculpture; he does not list individual works, define a corpus, or identify a specific sculpture collection. This unit does not expand the category into an object list. The Chinese title is a contextual working label. {p15}",
        [term_source],
        f"术语边界：仅指该处 source-local 的通类表达 “antique sculpture”，不主张其为穷尽性艺术史分类，也不据此推定某件作品、收藏规模或现存对象。{p15}\n\n本概念候选来自 `cand-12249`，其 S3 描述明确限定为 Maffei 收藏语境中的一般类别。",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Scipione Maffei and the antique-sculpture term in S4.")
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

    for item, expected_type in ((PERSON, "person"), (TERM, "term")):
        assert candidate_by_id[item["candidate"]]["suggested_type"] == expected_type
        decision = decision_by_id[item["candidate"]]
        assert decision["decision"] == "new" and not decision.get("ku_id")
        assert sync.get_group(decision.get("resolution_note", "")) == item["group"]
        members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new"
            and sync.get_group(row.get("resolution_note", "")) == item["group"]
        ]
        assert members == [item["candidate"]], (item["group"], members)
        assert not item["card_path"].exists()
        assert item["card_rel"] not in accepted
        assert not any(row.get("ku_id") == item["ku_id"] or row.get("card_path") == item["card_rel"] for row in manifest)
        assert not any(
            row["type"] == expected_type
            and (row.get("name_en", "").casefold() == item["name_en"].casefold()
                 or row.get("canonical_name", "").casefold() == item["name_zh"].casefold())
            for row in manifest
        ), f"duplicate same-name KU: {item['ku_id']}"

    statements = [
        json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    person_direct = {
        row["statement_id"] for row in statements
        if PERSON["candidate"] in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    }
    term_direct = {
        row["statement_id"] for row in statements
        if TERM["candidate"] in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    }
    assert person_direct == PERSON_STATEMENTS
    assert term_direct == {"st-chp15-p372-maffei-collected-antique-sculpture"}
    relation_candidates = {
        row["statement_id"] for row in statements
        if row["statement_id"] in PERSON_STATEMENTS
        and row.get("qualifiers", {}).get("relation_candidate") is True
    }
    assert relation_candidates == PERSON_STATEMENTS

    source_files = {
        "08_CHP-8_sec_ii.md": ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md",
        "10_CHP-10_sec_ii.md": ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md",
        "15_CHP-15_sec_ii.md": ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md",
    }
    quotes = [
        ("08_CHP-8_sec_ii.md", "He supported writers such as Apostolo Zeno,\nBenedetto Menzini and Scipione Maffei"),
        ("10_CHP-10_sec_ii.md", "Outside Venice he was in touch with Montesquieu and Scipione Maffei."),
        ("15_CHP-15_sec_ii.md", "Scipione Maffei who in an earlier generation had also collected antique sculpture and lovingly recorded the evidences of the past."),
    ]
    for filename, quote in quotes:
        assert quote in source_files[filename].read_text(encoding="utf-8-sig"), (filename, quote)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for item in (PERSON, TERM):
        planned_by_id[item["candidate"]]["ku_id"] = item["ku_id"]
        planned_by_id[item["candidate"]]["resolution_note"] += (
            f" S4 registration: mapped {item['group']} to {item['ku_id']}."
        )
    planned_manifest = list(manifest)
    for item in (PERSON, TERM):
        planned_manifest.append({
            "ku_id": item["ku_id"], "type": item["type"], "canonical_name": item["name_zh"],
            "name_en": item["name_en"], "source_task": TASK, "card_path": item["card_rel"],
        })

    stats = sync.summarize_by_type(candidate_rows, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidate_by_id)
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S4：Scipione Maffei 人物与古代雕塑术语端点登记（2026-10-16）\n\n"
        f"人物组 `{PERSON['group']}`（`{PERSON['candidate']}`）映射至[Scipione Maffei 人物卡]"
        "(../../../04-knowledge/units/persons/scipione-maffei.md)；"
        f"术语组 `{TERM['group']}`（`{TERM['candidate']}`）映射至[古代雕塑术语卡]"
        "(../../../04-knowledge/units/terms/antique-sculpture-maffei-context.md)。"
        "三章全名锚点支持同一人物组；p.230、p.320、p.372 的内容分别保留为 Haskell 对赞助、交往和收藏的书内陈述。"
        "Lodoli、Ferdinand de’ Medici 与 Angelo Querini 端点已有 KU；古代雕塑通类本批登记。5条关系候选均留待 S6，"
        "其中 `st-chp15-p372-maffei-recorded-evidence-of-the-past` 仍有未具体识别的开放对象端点，不据此新造对象；未修改 `relations.csv`。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4：Scipione Maffei 人物与古代雕塑术语登记（2026-10-16）\n\n"
        f"人物候选 `{PERSON['candidate']}` 登记为[Scipione Maffei 人物卡](../units/persons/scipione-maffei.md)；"
        f"`{TERM['candidate']}` 登记为[古代雕塑术语卡](../units/terms/antique-sculpture-maffei-context.md)。"
        "卡片保留书内三章人物锚点和术语通类边界。5条关系候选留待 S6；Lodoli、Ferdinand de’ Medici 与 Angelo Querini 已有 KU，"
        "古代雕塑端点已登记；“记录过去遗存”的对象仍未具体识别，保持开放，不新增正式关系。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    if args.dry_run:
        print("S4 Maffei registration dry-run passed")
        print(f"person: {PERSON['candidate']} -> {PERSON['ku_id']} ({len(person_direct)} direct statements)")
        print(f"term: {TERM['candidate']} -> {TERM['ku_id']} ({len(term_direct)} direct statement)")
        print(f"relation candidates retained for S6: {len(relation_candidates)}; formal relation writes: 0")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}")
        print(
            f"registered={sync.fmt(totals['registered_groups'])} groups/{sync.fmt(totals['registered_members'])} candidates; "
            f"pending={sync.fmt(totals['pending_groups'])} groups/{sync.fmt(totals['pending_members'])} candidates"
        )
        print("S3 groups, source quotations, candidate types, direct endpoints, and destination uniqueness checked; no files changed")
        return 0

    PERSON["card_path"].write_text(person_card(), encoding="utf-8-sig", newline="\n")
    TERM["card_path"].write_text(term_card(), encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    for item in sorted((PERSON, TERM), key=lambda record: record["card_rel"]):
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
        f"applied: person={PERSON['ku_id']}; term={TERM['ku_id']}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
