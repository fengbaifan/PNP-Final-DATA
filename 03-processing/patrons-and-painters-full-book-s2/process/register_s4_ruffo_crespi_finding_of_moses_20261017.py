from __future__ import annotations

import argparse
import difflib
import io
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
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

CANDIDATE = "cand-7720"
GROUP = "workgrp-ruffo-crespi-finding-of-moses-p222"
KU_ID = "units/works/giuseppe-maria-crespi-finding-of-moses-ruffo-commission"
CARD_REL = "04-knowledge/units/works/giuseppe-maria-crespi-finding-of-moses-ruffo-commission.md"
CARD_PATH = ROOT / CARD_REL
DATE = "2026-10-17"
S4_ANCHOR = "s4-ruffo-crespi-finding-of-moses-registration-20261017"
S3_ANCHOR = "s3-crespi-finding-moses-same-title-split-20261017"
S3_PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{S3_ANCHOR}"
S4_PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{S4_ANCHOR}"
STMT_ID = "st-chp8-p222-ruffo-commissioned-finding-of-moses"
CONTl_KU = "units/works/g-m-crespi-jupiter-handed-over-by-cybele-to-the-corybantes-to-be-fed"
CONTl_CARD = "04-knowledge/units/works/g-m-crespi-jupiter-handed-over-by-cybele-to-the-corybantes-to-be-fed.md"
RUFFO_KU = "units/persons/tommaso-ruffo"
CRESPI_KU = "units/persons/giuseppe-maria-crespi"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCE_CH8 = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
NAME_ZH = "朱塞佩·马里亚·克雷斯皮为托马索·鲁福所作《摩西的发现》"
NAME_EN = "Giuseppe Maria Crespi, The Finding of Moses for Cardinal Tommaso Ruffo"

QUOTE_P222 = (
    "Crespi was represented by four works, two of which were commissioned during Russo’s legateship in the city: "
    "Abigail giving Presenti to David and The Finding of Moses.5 Both these religious themes are treated in a spirit of subdued and tender romanticism."
)
QUOTE_P228 = (
    "The Infant Jupiter handed over by Cybele to the Corybantes to be fed (Plate 67)"
    " ... when sending the painting itself in April 1729, he changed the title to The Finding of Moses, "
    "as sacred pictures paid lower customs duty than profane ones!"
)
QUOTE_P405 = (
    "Stefano Conti’s last commission—a picture by Crespi of Jupiter among the Corybantes, cunningly described by him as "
    "The Finding of Moses because, as a sacred subject, it would pay less customs duty"
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    old = path.read_bytes() if path.exists() else b""
    bom = b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
    path.write_bytes(bom + text.encode("utf-8"))


def show_diff(path: str, old: str, new: str) -> None:
    diff = difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f"a/{path}", tofile=f"b/{path}",
    )
    print("".join(diff), end="")


def render_csv(fieldnames, rows) -> str:
    import csv

    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第8章；印刷页222；Markdown L134–135",
            "sentence_summary": (
                "Haskell称 Crespi 的四件作品中有两件在其所称 ‘Russo’ 的任使期间受委托，其中一件题为 The Finding of Moses；"
                "S2依据原页图将此处OCR形式 Russo 校正为 Ruffo。段落未给该画的具体年份、媒材或现藏地点。"
            ),
            "original_quotes": [
                {"source_span": "L134–135; print p. 222", "text": QUOTE_P222},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_CH8,
                "source_span": "L134–135; print p. 222",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第8章；印刷页228；Markdown L209–211",
            "sentence_summary": (
                "Haskell identifies a separate Stefano Conti commission as the Jupiter/Cybele painting and says Crespi used "
                "The Finding of Moses as its shipping title to reduce customs duty."
            ),
            "original_quotes": [
                {"source_span": "L209–211; print p. 228", "text": QUOTE_P228},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_CH8,
                "source_span": "L209–211; print p. 228",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第20章后记；印刷页405；Markdown L138",
            "sentence_summary": (
                "Haskell's postscript restates that the Conti commission was a Jupiter/Corybantes picture carrying The Finding of Moses "
                "as a customs-duty description; it is the work separately represented by Plate 67."
            ),
            "original_quotes": [
                {"source_span": "L138; print p. 405", "text": QUOTE_P405},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "source_span": "L138; print p. 405",
            },
        },
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "work",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": S4_PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p222 = f"[第8章 p.222](../../../{SOURCE_CH8}#L134)"
    p228 = f"[第8章 p.228](../../../{SOURCE_CH8}#L209)"
    p405 = "[第20章 p.405](../../../02-sources/02-Markdown/20_CHP-20Postscript.md#L138)"
    conti_link = f"[Conti 的 Jupiter/Cybele 画]({Path(CONTl_CARD).name})"
    ruffo_link = "[托马索·鲁福（Cardinal Tommaso Ruffo）](../persons/tommaso-ruffo.md)"
    crespi_link = "[朱塞佩·马里亚·克雷斯皮（Giuseppe Maria Crespi）](../persons/giuseppe-maria-crespi.md)"
    body = f"""## 内容

### 描述

**中文：** 本卡记录哈斯克尔第8章 p.222 所列、题为 The Finding of Moses 的一件 Crespi 画作。原书将它列为 Cardinal Tommaso Ruffo 任使期间委托的两件宗教题材作品之一；来源 OCR 作 “Russo”，S2 已依据原页图校正为 “Ruffo”。该段没有给出本画的创作年份、媒材或现藏地点。题名与 Conti 的 Jupiter/Cybele 画相同，但二者是不同作品；本画按 p.222 的独立委托项目登记。中文名是描述性译名。{p222}

**English:** This card records the Crespi painting titled *The Finding of Moses* on p. 222. Haskell lists it among two religious works commissioned during Cardinal Tommaso Ruffo’s legateship. The source OCR reads “Russo”; an S2 page-image review corrected the name to “Ruffo.” The passage gives no creation date, medium, or present location for this painting. Although it shares a title with Conti’s Jupiter/Cybele painting, they are distinct works; this card follows the separate commission listed on p. 222. The Chinese display name is descriptive. {p222}

### 名称

书中题名为 *The Finding of Moses*。卡片英文显示名加入画家与委托语境以作消歧；中文显示名为描述性译名。{p222}

### 基本信息

- **作品类型：** 绘画。{p222}
- **书中作者归属：** {crespi_link}；Haskell将该画列入 Crespi 的四件作品。{p222}
- **委托语境：** {ruffo_link} 任使期间委托的两件作品之一；具体年份未载。OCR 姓名校正见 S2 过程记录。{p222}

### 本章相关内容

Haskell称 p.222 所列两件宗教题材画以克制、温和的浪漫主义方式处理。此描述按作者原有范围保留，不外推为本画的独立风格定论。{p222}

### 身份边界

第8章 p.228 和第20章后记 p.405 所称的另一件画是 Stefano Conti 委托的 Jupiter/Cybele 题材作品；Haskell明确解释《The Finding of Moses》在该画上是为降低关税而使用的发货题名。该画见{conti_link}。此处的 p.222 作品属于另一项委托，题名相同不构成同一作品证据。{p228}；{p405}

## 关系与证据

### 关系记录

本卡没有新增正式关系。书内关于委托与作者归属的陈述保留在 S2 关系候选中，待 S6 审查：

- `{STMT_ID}`

本卡仅依据书内来源登记；未对这件 p.222 作品作外部身份、日期、材质或现藏核验。
"""
    return f"---\n{fm}---\n\n{body}"


def add_accepted_path(text: str) -> str:
    lines = text.splitlines()
    target = f"- {CARD_REL}"
    assert target not in lines
    units_end = next((i for i, line in enumerate(lines) if line.startswith("claims:")), len(lines))
    unit_lines = [line for line in lines[:units_end] if line.startswith("- 04-knowledge/units/")]
    assert CARD_REL not in {line[2:] for line in unit_lines}
    insert_at = next(
        (i for i, line in enumerate(lines[:units_end])
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        units_end,
    )
    lines.insert(insert_at, target)
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the distinct p.222 Crespi Finding of Moses work in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert CANDIDATE in candidate_by_id and candidate_by_id[CANDIDATE]["suggested_type"] == "work"
    assert alignment_by_id[CANDIDATE]["decision"] == "new"
    assert sync.get_group(alignment_by_id[CANDIDATE].get("resolution_note", "")) == GROUP
    group_members = {
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == {CANDIDATE}
    assert alignment_by_id["cand-0879"]["decision"] == "same"
    assert alignment_by_id["cand-0879"]["ku_id"] == CONTl_KU

    registered_rows = [row for row in manifest if row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL]
    name_rows = [row for row in manifest if row.get("type") == "work" and (row.get("name_en") or "").casefold() == NAME_EN.casefold()]
    accepted_text = read_text(ACCEPTED_PATH)
    accepted_paths = {line[2:] for line in accepted_text.splitlines() if line.startswith("- 04-knowledge/units/")}
    registered = (
        len(registered_rows) == 1 and registered_rows[0].get("ku_id") == KU_ID
        and alignment_by_id[CANDIDATE].get("ku_id") == KU_ID
        and CARD_REL in accepted_paths and CARD_PATH.exists()
    )
    assert len(registered_rows) <= 1 and len(name_rows) <= 1
    if registered:
        assert len(name_rows) == 1 and name_rows[0].get("ku_id") == KU_ID
        assert f"S4 registration: mapped {GROUP} to {KU_ID}." in alignment_by_id[CANDIDATE].get("resolution_note", "")
        expected_card = make_card()
        current_card = read_text(CARD_PATH)
        if current_card != expected_card:
            print(f"CARD UPDATE REQUIRED: {CARD_REL}; registration and identity mapping are already applied.")
            if args.dry_run:
                show_diff(CARD_REL, current_card, expected_card)
                return 0
            write_text(CARD_PATH, expected_card)
            print("CARD UPDATED: removed hand-authored tables; source-backed facts remain as evidence-linked prose and list items.")
            return 0
        print(f"ALREADY REGISTERED: {CANDIDATE} -> {KU_ID}; one S2 relation candidate remains for S6.")
        return 0
    assert not registered_rows and not name_rows and not alignment_by_id[CANDIDATE].get("ku_id")
    assert CARD_REL not in accepted_paths and not CARD_PATH.exists()

    source = " ".join((ROOT / SOURCE_CH8).read_text(encoding="utf-8-sig").split())
    postscript = " ".join((ROOT / "02-sources/02-Markdown/20_CHP-20Postscript.md").read_text(encoding="utf-8-sig").split())
    assert "Crespi was represented by four works, two of which were commissioned during Russo’s legateship" in source
    assert "Abigail giving Presenti to David and The Finding of Moses" in source
    assert "The Infant Jupiter handed over by Cybele to the Corybantes to be fed" in source
    assert "changed the title to The Finding of Moses, as sacred pictures paid lower customs duty" in source
    assert "Stefano Conti’s last commission—a picture by Crespi of Jupiter among the Corybantes" in postscript
    statements = sync.load_statements()
    actual_relations = {
        row["statement_id"] for row in statements
        if CANDIDATE in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert actual_relations == {STMT_ID}, actual_relations

    existing_process = read_text(PROCESS_PATH)
    existing_result = read_text(RESULT_PATH)
    assert S3_ANCHOR in existing_process and S4_ANCHOR not in existing_process
    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignments if row.get("candidate_id")}
    row = planned_by_id[CANDIDATE]
    row["ku_id"] = KU_ID
    row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "work",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(values[key] for values in stats.values()) for key in next(iter(stats.values()))}
    new_result = sync.update_result(existing_result, stats, totals, len(planned_manifest)).rstrip()
    new_result += (
        "\n\n### S4 work：Crespi《The Finding of Moses》（Ruffo 委托语境）登记（2026-10-17）\n\n"
        f"`{CANDIDATE}`（`{GROUP}`）登记为[作品卡](../units/works/{Path(CARD_REL).name})。它与已复用至既有 Conti Jupiter/Cybele 作品卡的 `cand-0879` 分属两件作品，"
        "仅共用《The Finding of Moses》题名。卡片保存 p.222 委托语境及 p.228/p.405 的身份区分；一条直接 S2 关系候选仍待 S6，未新增正式关系。\n\n"
        f"S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    new_process = existing_process.rstrip() + (
        f"\n\n<a id=\"{S4_ANCHOR}\"></a>\n\n"
        "### S4 work：Ruffo 任使期间受委托的 Crespi《The Finding of Moses》登记（2026-10-17）\n\n"
        f"`{CANDIDATE}` 在 S3 更正后作为独立新作品组 `{GROUP}`，登记为 [作品卡](../../../{CARD_REL})。第8章 p.222 将其列为 Crespi 的作品之一及 Ruffo 任使期间委托的宗教题材画；OCR 的 Russo 依 S2 页图核对校正为 Ruffo。第8章 p.228 与第20章 p.405 所述 Conti Jupiter/Cybele 画虽然用了同一《The Finding of Moses》发货题名，但身份不同，映射至既有工作 KU 的候选 `cand-0879` 已改为 `same`。\n\n"
        f"卡片不补写 `{CANDIDATE}` 的具体创作年份、媒材、现藏地或外部身份。`{STMT_ID}` 仍为 S2 关系候选，待 S6；本批未写入正式关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    new_accepted = add_accepted_path(accepted_text)
    new_card = make_card()

    if args.dry_run:
        print(f"S4: register {GROUP} -> {KU_ID}; candidate={CANDIDATE}; relation candidates pending S6={len(actual_relations)}.")
        print(f"Counts: registered groups={totals['registered_groups']}, members={totals['registered_members']}; "
              f"pending groups={totals['pending_groups']}, members={totals['pending_members']}; KU={len(planned_manifest)}.")
        print("Planned files: alignment.csv, ku-manifest.csv, accepted.yml, work card, process/knowledge.md, result.")
        print("\n--- Reviewable diff ---")
        show_diff("04-knowledge/tables/alignment.csv", render_csv(alignment_fields, alignments), render_csv(alignment_fields, planned_alignments))
        show_diff("04-knowledge/tables/ku-manifest.csv", render_csv(manifest_fields, manifest), render_csv(manifest_fields, planned_manifest))
        show_diff("04-knowledge/accepted.yml", accepted_text, new_accepted)
        show_diff(CARD_REL, "", new_card)
        show_diff("03-processing/" + TASK + "/process/knowledge.md", existing_process, new_process)
        show_diff("04-knowledge/results/" + TASK + ".md", existing_result, new_result)
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_text(ACCEPTED_PATH, new_accepted)
    write_text(CARD_PATH, new_card)
    write_text(PROCESS_PATH, new_process)
    write_text(RESULT_PATH, new_result)
    print(f"APPLIED: {CANDIDATE} -> {KU_ID}; one relation candidate remains pending S6.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
