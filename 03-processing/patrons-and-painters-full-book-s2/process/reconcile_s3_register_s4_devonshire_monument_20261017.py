from __future__ import annotations

import argparse
import csv
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
CARD_REL = "04-knowledge/units/works/mcswiny-duke-of-devonshire-monument.md"
CARD_PATH = ROOT / CARD_REL
KU_ID = "units/works/mcswiny-duke-of-devonshire-monument"
GROUP = "workgrp-812459889b2b31"
CID = "cand-9016"
DATE = "2026-10-17"
S3_ANCHOR = "s3-work-devonshire-monument-adjudication-20261017"
S4_ANCHOR = "s4-work-devonshire-monument-registration-20261017"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCE_BODY = "02-sources/02-Markdown/10_CHP-10_intro.md"
SOURCE_TABLE = "02-sources/02-Markdown/10_CHP-10_intro_notes_p289_visual-transcription.md"
QUOTE_BODY = (
    "But Sebastiano and Marco Ricci who collaborated on the monument to the Duke of Devonshire "
    "were already wellestablished painters and must have required a substantial fee to produce "
    "such menial work for a commoner."
)
QUOTE_TABLE = "| Marco Ricci; Sebastiano Ricci | Duke of Devonshire | Barber Institute |"
QUOTE_VERSION = (
    "2 The Duke of Devonshire thus altered must be another version of the one which once belonged "
    "to the Duke of Richmond and is now in the Barber Institute. The one of Sir Cloudesly Shovel "
    "has not yet been traced, but this too must have been a second version of the one belonging to "
    "the Duke of Richmond."
)
RELATION_IDS = (
    "st-chp10-p289-devonshire-monument-subject",
    "st-chp10-p289-marco-ricci-collaborated",
    "st-chp10-p289-note1-row02-artist1",
    "st-chp10-p289-note1-row02-artist2",
    "st-chp10-p289-note1-row02-subject",
    "st-chp10-p289-sebastiano-ricci-collaborated",
    "st-chp10-p290-note2-devonshire-alternate-version",
)
NAME_ZH = "麦克斯温尼方案中的德文郡公爵纪念画"
NAME_EN = "McSwiny’s Monument to the Duke of Devonshire"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    old = path.read_bytes() if path.exists() else b""
    bom = b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
    path.write_bytes(bom + text.encode("utf-8"))


def render_csv(fieldnames, rows) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def show_diff(path: str, old: str, new: str) -> None:
    diff = difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile=f"a/{path}",
        tofile=f"b/{path}",
    )
    print("".join(diff), end="")


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第10章；印刷页289；Markdown L230",
            "sentence_summary": (
                "Haskell称 McSwiny 方案中有一幅德文郡公爵纪念画，并说 Sebastiano 与 Marco Ricci 参与其制作；"
                "这是书内叙述，尚未独立核实作品身份或作者角色。"
            ),
            "original_quotes": [{"source_span": "L230; print p. 289", "text": QUOTE_BODY}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_BODY,
                "source_span": "L230; print p. 289",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章；印刷页289；注1表第2行；转录文件 L6",
            "sentence_summary": (
                "注1表将 Marco Ricci 与 Sebastiano Ricci 列在 artists 栏，将 Duke of Devonshire 列作该行题材，"
                "并带有 Barber Institute 括号标记；该标记不证明当前馆藏。"
            ),
            "original_quotes": [{"source_span": "L6; note 1, print p. 289", "text": QUOTE_TABLE}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_TABLE,
                "source_span": "L6; note 1, print p. 289",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章；印刷页290；注2；Markdown L546",
            "sentence_summary": (
                "Haskell 推断 Bingley 改绘的 Devonshire 画是曾属 Richmond、并称当时在 Barber Institute 的另一版本；"
                "这是作者的版本推断，不等同于本项目确认两件作品的身份或当前馆藏。"
            ),
            "original_quotes": [{"source_span": "L546; note 2, print p. 290", "text": QUOTE_VERSION}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_BODY,
                "source_span": "L546; note 2, print p. 290",
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
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{S4_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body_link = f"[第10章 p.289](../../../{SOURCE_BODY}#L230)"
    table_link = f"[注1表第2行](../../../{SOURCE_TABLE}#L6)"
    version_link = f"[第10章注2](../../../{SOURCE_BODY}#L546)"
    card_body = f"""## 内容

### 描述

**中文：** 本卡登记 Haskell 在 McSwiny 英国名人绘画方案中提到的一幅无题作品，原文称为 “monument to the Duke of Devonshire”。正文称 Sebastiano 与 Marco Ricci 参与其制作；注1表把两人列在 artists 栏，并将 Duke of Devonshire 列为题材。表内的 Barber Institute 是原书标注，不确认当前馆藏；书内作者角色仍是 S2 关系候选，待 S6 裁决。中文显示名为描述性工作题名。{body_link}；{table_link}

**English:** This card records an untitled work mentioned by Haskell within McSwiny’s scheme of British worthies, called in the text a “monument to the Duke of Devonshire.” The passage says Sebastiano and Marco Ricci participated in its making; note 1 lists both in the artists column and gives the Duke of Devonshire as the subject. “Barber Institute” is a label in Haskell’s table and does not establish current custody. The book’s artist-role claims remain S2 relation candidates for S6 adjudication. The English and Chinese names are descriptive working titles. {body_link}; {table_link}

### 作品身份与版本边界

- 原书没有提供正式作品题名或日期；本卡名称为描述性工作题名。{body_link}
- 注1表的 Barber Institute 括号标记按原书语境保留，不作为当前收藏地点核验。{table_link}
- Haskell 在注2推断 Bingley 改绘的 Devonshire 画是另一版本；该推断没有识别该版本的具体对象。本卡只映射 `cand-9016`，`cand-9020` 仍为 S3 `undecided`，不合并入本卡。{version_link}
- 本卡指绘画方案中的一件作品，不指整个寓意墓画系列，也不把系列题名或“monument”译作一座实体墓葬或建筑。

## 关系与证据

### 关系记录

本卡没有新增正式关系。以下7条直接相关的S2关系候选仍留待S6逐条审查端点、角色和作者限定：

{chr(10).join(f'- `{sid}`' for sid in RELATION_IDS)}
"""
    return f"---\n{fm}---\n\n{card_body}"


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
    parser = argparse.ArgumentParser(description="Adjudicate and register the Devonshire monument work endpoint.")
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
    assert CID in candidate_by_id and CID in alignment_by_id
    candidate = candidate_by_id[CID]
    alignment = alignment_by_id[CID]
    assert candidate["suggested_type"] == "work"
    assert candidate["canonical_name"] == "McSwiny's monument to the Duke of Devonshire (untitled)"
    assert candidate["candidate_source_ref"] == "chp-10:10_CHP-10_intro:l229-238#L230"
    assert alignment["decision"] == "new" and sync.get_group(alignment.get("resolution_note", "")) == GROUP

    group_members = {
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == {CID}, group_members
    assert alignment_by_id["cand-9020"]["decision"] == "undecided"
    assert not sync.get_group(alignment_by_id["cand-9020"].get("resolution_note", ""))

    statements = sync.load_statements()
    actual_relations = {
        row["statement_id"] for row in statements
        if CID in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert actual_relations == set(RELATION_IDS), actual_relations
    body_text = " ".join((ROOT / SOURCE_BODY).read_text(encoding="utf-8-sig").split())
    table_text = " ".join((ROOT / SOURCE_TABLE).read_text(encoding="utf-8-sig").split())
    assert " ".join(QUOTE_BODY.split()) in body_text
    assert " ".join(QUOTE_TABLE.split()) in table_text
    assert " ".join(QUOTE_VERSION.split()) in body_text

    registered_rows = [row for row in manifest if row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL]
    same_name_rows = [
        row for row in manifest
        if row.get("type") == "work" and (row.get("name_en") or "").casefold() == NAME_EN.casefold()
    ]
    accepted_text = read_text(ACCEPTED_PATH)
    accepted_paths = {
        line[2:] for line in accepted_text.splitlines()
        if line.startswith("- 04-knowledge/units/")
    }
    registered = (
        len(registered_rows) == 1 and registered_rows[0].get("ku_id") == KU_ID
        and alignment.get("ku_id") == KU_ID and CARD_REL in accepted_paths and CARD_PATH.exists()
    )
    assert len(registered_rows) <= 1 and len(same_name_rows) <= 1
    if registered:
        assert len(same_name_rows) == 1 and same_name_rows[0].get("ku_id") == KU_ID
        assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
        assert f"S4 registration: mapped {GROUP} to {KU_ID}." in alignment.get("resolution_note", "")
        print(f"ALREADY REGISTERED: {CID} -> {KU_ID}; {len(actual_relations)} relation candidates remain for S6.")
        return 0
    assert not same_name_rows
    assert not registered_rows and not alignment.get("ku_id") and CARD_REL not in accepted_paths and not CARD_PATH.exists()

    source_files = {SOURCE_BODY, SOURCE_TABLE}
    assert source_files == {SOURCE_BODY, SOURCE_TABLE}
    existing_process = read_text(PROCESS_PATH)
    existing_result = read_text(RESULT_PATH)
    assert S3_ANCHOR not in existing_process and S4_ANCHOR not in existing_process

    planned_alignments = [dict(row) for row in alignments]
    planned_alignment_by_id = {row["candidate_id"]: row for row in planned_alignments if row.get("candidate_id")}
    planned_target = planned_alignment_by_id[CID]
    planned_target["resolution_note"] = (
        "source_ref=entity-candidates.csv#cand-9016;candidate_source_ref="
        "chp-10:10_CHP-10_intro:l229-238#L230;mentions=m-chp10-p289-monument,"
        "m-chp10-p290-notes-n2-devonshire-richmond-version;segments="
        "chp-10:10_CHP-10_intro:l229-238,chp-10:10_CHP-10_intro:l491-634; "
        f"group={GROUP}; 判为new：第10章p.289正文及注1表共同支持McSwiny方案中一幅未具正式题名的德文郡公爵纪念画；"
        "现有manifest无可对应的work KU。p.290注2提出Bingley改绘画面的另一版本推断，但未确证具体对象身份；"
        "cand-9020继续undecided，不并组。本决定限于书内身份锚点，未作外部身份核验或正式作者关系裁决。"
    )
    planned_target["ku_id"] = KU_ID
    planned_target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

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
        "\n\n### work：McSwiny 德文郡公爵纪念画 S3/S4 裁决与登记（2026-10-17）\n\n"
        f"`{CID}` 判为 `{GROUP}` 的单件新作品组并登记至[作品卡](../units/works/mcswiny-duke-of-devonshire-monument.md)。"
        "p.289正文和注1表为身份依据；描述性题名、作品版本及原书表格的 Barber Institute 标记均按来源范围限定。"
        "`cand-9020` 的Bingley改绘版本仍为 `undecided`，未合并；7条直接S2关系候选留待S6，未新增正式关系。"
        "没有进行外部身份或现藏核验。\n\n"
        f"全书S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    new_process = existing_process.rstrip() + (
        f"\n\n<a id=\"{S3_ANCHOR}\"></a>\n\n"
        "### S3 work：McSwiny 德文郡公爵纪念画与改绘版本区分（2026-10-17）\n\n"
        f"`{CID}` 的正文锚点为第10章 p.289 L230，注1表的同项行位于转录文件 L6；两处相合，将其裁决为 McSwiny 方案中的一幅单件、无正式题名作品，归入唯一新组 `{GROUP}`。"
        "现有 manifest 无对应 work KU，因此决定为 `new`。第10章 p.290 注2将 Bingley 改绘的 Devonshire 画推断为另一版本；其具体对象与版本身份未被识别，`cand-9020` 保持 `undecided`，不并入本组。未作外部身份核验；原书对 Ricci 参与的陈述仍按 S2 关系候选留待 S6。\n\n"
        f"<a id=\"{S4_ANCHOR}\"></a>\n\n"
        "### S4 work：McSwiny 德文郡公爵纪念画登记（2026-10-17）\n\n"
        f"`{CID}`（`{GROUP}`）登记为单个 work KU：[作品卡](../../../{CARD_REL})。卡片保存第10章 p.289 正文、注1表及 p.290 注2的来源范围，标明无正式题名、描述性工作题名和版本边界。"
        f"7条直接S2关系候选仍待S6：{', '.join(f'`{sid}`' for sid in RELATION_IDS)}。没有新增正式关系或外部身份断言。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    new_accepted = add_accepted_path(accepted_text)
    new_card = make_card()

    if args.dry_run:
        print(f"S3: {CID} -> new group {GROUP}; cand-9020 remains undecided.")
        print(f"S4: add {KU_ID} ({CARD_REL}); 7 direct relation candidates remain for S6.")
        print(f"Counts: registered groups={totals['registered_groups']}, members={totals['registered_members']}, "
              f"pending groups={totals['pending_groups']}, members={totals['pending_members']}, "
              f"KU={len(planned_manifest)}.")
        print("Planned files: alignment.csv, ku-manifest.csv, accepted.yml, new work card, process/knowledge.md, result.")
        old_alignment = render_csv(alignment_fields, alignments)
        new_alignment = render_csv(alignment_fields, planned_alignments)
        old_manifest = render_csv(manifest_fields, manifest)
        new_manifest = render_csv(manifest_fields, planned_manifest)
        print("\n--- Reviewable diff ---")
        show_diff("04-knowledge/tables/alignment.csv", old_alignment, new_alignment)
        show_diff("04-knowledge/tables/ku-manifest.csv", old_manifest, new_manifest)
        show_diff("04-knowledge/accepted.yml", accepted_text, new_accepted)
        show_diff("04-knowledge/units/works/mcswiny-duke-of-devonshire-monument.md", "", new_card)
        show_diff("03-processing/patrons-and-painters-full-book-s2/process/knowledge.md", existing_process, new_process)
        show_diff("04-knowledge/results/patrons-and-painters-full-book-s2.md", existing_result, new_result)
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_text(ACCEPTED_PATH, new_accepted)
    write_text(CARD_PATH, new_card)
    write_text(PROCESS_PATH, new_process)
    write_text(RESULT_PATH, new_result)
    print(f"APPLIED: S3 {CID} -> {GROUP}; S4 {KU_ID}; 7 relation candidates pending S6.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
