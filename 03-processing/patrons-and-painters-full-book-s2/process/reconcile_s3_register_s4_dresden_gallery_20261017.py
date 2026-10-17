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
CARD_REL = "04-knowledge/units/institutions/dresden-gallery.md"
CARD_PATH = ROOT / CARD_REL
KU_ID = "units/institutions/dresden-gallery"
GROUP = "sg3-institution-dresden-gallery"
CID = "cand-9091"
PENDING_CID = "cand-10222"
DATE = "2026-10-17"
S3_ANCHOR = "s3-dresden-gallery-scope-adjudication-20261017"
S4_ANCHOR = "s4-dresden-gallery-registration-20261017"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCE_CH10 = "02-sources/02-Markdown/10_CHP-10_intro.md"
SOURCE_CH14 = "02-sources/02-Markdown/14_CHP-14_intro.md"
QUOTE_GUARIENTI = (
    "under the direction of a Venetian artist,\nPietro Guarienti, the Dresden Gallery achieved its great "
    "pre-eminence over nearly all the others in Germany."
)
QUOTE_PLAN = (
    "In that year, in Dresden, he drew up a plan for extending and completing the spectacular art gallery "
    "which was being formed by Augustus of Saxony.2"
)
QUOTE_GALLERY_AIM = "He wants the gallery to reflect the whole history of painting and to include the finest representatives of all schools."
RELATION_IDS = (
    "st-chp10-p294-guarienti-dresden-gallery",
    "st-chp14-p350-dresden-gallery-plan",
    "st-chp14-p350-gallery-represent-history-and-schools",
)
NAME_ZH = "德累斯顿绘画馆"
NAME_EN = "Dresden Gallery"


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
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f"a/{path}", tofile=f"b/{path}",
    )
    print("".join(diff), end="")


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第10章；印刷页294；Markdown L298–299",
            "sentence_summary": (
                "Haskell称威尼斯艺术家 Pietro Guarienti 领导下的 Dresden Gallery 在德国画廊中达到显著地位；"
                "这是作者的评价，不是量化排名。"
            ),
            "original_quotes": [{"source_span": "L298–299; print p. 294", "text": QUOTE_GUARIENTI}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_CH10,
                "source_span": "L298–299; print p. 294",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第14章；印刷页350；Markdown L39",
            "sentence_summary": (
                "Haskell称 Algarotti 于1742年在 Dresden 制定扩充并完成 Augustus of Saxony 正在形成的绘画馆的计划，"
                "并希望其呈现绘画史及各画派代表作品；该方案不证明后来全部实施。"
            ),
            "original_quotes": [
                {"source_span": "L39; print p. 350", "text": QUOTE_PLAN},
                {"source_span": "L39; print p. 350", "text": QUOTE_GALLERY_AIM},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_CH14,
                "source_span": "L39; print p. 350",
            },
        },
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "institution",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{S4_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch10_link = f"[第10章 p.294](../../../{SOURCE_CH10}#L298)"
    ch14_link = f"[第14章 p.350](../../../{SOURCE_CH14}#L39)"
    body = f"""## 内容

### 描述

**中文：** 本卡登记 Haskell 所称的 Dresden Gallery 这一绘画馆机构。第10章称其在 Pietro Guarienti 领导下取得显著地位；第14章记 Algarotti 于1742年为 Augustus of Saxony 正在形成的绘画馆拟定扩充与完成计划，并希望馆藏呈现绘画史和各画派代表。该计划为方案，不表示全部实施；Guarienti 的职责仍为S2关系候选，留待S6裁决。中文名为描述性译名。{ch10_link}；{ch14_link}

**English:** This card records the art-gallery institution Haskell calls the Dresden Gallery. Chapter 10 says it achieved prominence under Pietro Guarienti; Chapter 14 reports that in 1742 Algarotti planned to extend and complete the gallery being formed by Augustus of Saxony and wanted it to represent the history of painting and leading works of all schools. The plan does not establish full implementation. Guarienti’s role remains an S2 relation candidate for S6 adjudication. The Chinese name is a descriptive translation. {ch10_link}; {ch14_link}

### 机构信息

- **机构性质：** Haskell 称其为 Dresden 的绘画馆（art gallery）；本卡记录机构，不指认具体馆舍建筑。{ch14_link}
- **管理与地位：** Haskell 称 Pietro Guarienti 领导下的 Dresden Gallery 在德国画廊中取得显著地位；这是作者评价。{ch10_link}
- **扩充方案：** Haskell 称 Algarotti 于1742年拟定扩充并完成 Augustus of Saxony 正在形成的绘画馆的计划；提出按绘画史及画派代表组织馆藏，未据此断言计划全部实施。{ch14_link}

### 身份边界

本卡指绘画馆机构，不等同于 Augustus III 的个人绘画收藏、某组具体画作或实体建筑。`cand-10222` 当前同时承载第14章 p.347 “royal gallery”及 p.355 “royal collection”等不同表述，S3 暂列 `undecided`，故本卡不映射该候选，也不据此合并收藏对象。

## 关系与证据

### 关系记录

本卡没有新增正式关系。以下3条直接相关的S2关系候选仍留待S6核对方向、角色及方案实施限定：

{chr(10).join(f'- `{sid}`' for sid in RELATION_IDS)}
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
    parser = argparse.ArgumentParser(description="Split an ambiguous Dresden gallery candidate and register the clear institution group.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    _, mentions = sync.read_csv(TABLES / "mentions.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert CID in candidate_by_id and PENDING_CID in candidate_by_id
    assert candidate_by_id[CID]["suggested_type"] == "institution"
    assert candidate_by_id[PENDING_CID]["suggested_type"] == "institution"
    assert alignment_by_id[CID]["decision"] == "new"
    assert alignment_by_id[PENDING_CID]["decision"] in {"new", "undecided"}

    group_members = {
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == {CID, PENDING_CID} or group_members == {CID}, group_members
    mention_ids = {row["mention_id"]: row for row in mentions}
    assert mention_ids["m-s2-ch14-p347-006"]["candidate_id"] == PENDING_CID
    assert mention_ids["m-chp14-p355-0037"]["candidate_id"] == PENDING_CID
    assert "royal collection" in mention_ids["m-chp14-p355-0037"]["surface_form"]
    actual_relations = {
        row["statement_id"] for row in sync.load_statements()
        if CID in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert actual_relations == set(RELATION_IDS), actual_relations
    ch10 = " ".join((ROOT / SOURCE_CH10).read_text(encoding="utf-8-sig").split())
    ch14 = " ".join((ROOT / SOURCE_CH14).read_text(encoding="utf-8-sig").split())
    for quote in (QUOTE_GUARIENTI,):
        assert " ".join(quote.split()) in ch10
    for quote in (QUOTE_PLAN, QUOTE_GALLERY_AIM):
        assert " ".join(quote.split()) in ch14

    registered_rows = [row for row in manifest if row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL]
    name_rows = [row for row in manifest if row.get("type") == "institution" and (row.get("name_en") or "").casefold() == NAME_EN.casefold()]
    accepted_text = read_text(ACCEPTED_PATH)
    accepted_paths = {line[2:] for line in accepted_text.splitlines() if line.startswith("- 04-knowledge/units/")}
    registered = (
        len(registered_rows) == 1 and registered_rows[0].get("ku_id") == KU_ID
        and alignment_by_id[CID].get("ku_id") == KU_ID
        and alignment_by_id[PENDING_CID]["decision"] == "undecided"
        and not sync.get_group(alignment_by_id[PENDING_CID].get("resolution_note", ""))
        and CARD_REL in accepted_paths and CARD_PATH.exists()
    )
    assert len(registered_rows) <= 1 and len(name_rows) <= 1
    if registered:
        assert len(name_rows) == 1 and name_rows[0].get("ku_id") == KU_ID
        assert sync.get_group(alignment_by_id[CID].get("resolution_note", "")) == GROUP
        assert f"S4 registration: mapped {GROUP} to {KU_ID}." in alignment_by_id[CID].get("resolution_note", "")
        print(f"ALREADY REGISTERED: {CID} -> {KU_ID}; {PENDING_CID} remains undecided; {len(actual_relations)} relation candidates remain for S6.")
        return 0
    assert not registered_rows and not name_rows and not alignment_by_id[CID].get("ku_id")
    assert CARD_REL not in accepted_paths and not CARD_PATH.exists()
    assert alignment_by_id[PENDING_CID]["decision"] == "new"
    assert sync.get_group(alignment_by_id[PENDING_CID].get("resolution_note", "")) == GROUP

    existing_process = read_text(PROCESS_PATH)
    existing_result = read_text(RESULT_PATH)
    assert S3_ANCHOR not in existing_process and S4_ANCHOR not in existing_process
    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignments if row.get("candidate_id")}
    target = planned_by_id[CID]
    target["resolution_note"] = (
        "source_ref=chp-10:10_CHP-10_intro:l292-302#L299; statements="
        "st-chp10-p294-guarienti-dresden-gallery,st-chp14-p350-dresden-gallery-plan,"
        "st-chp14-p350-gallery-represent-history-and-schools; "
        f"group={GROUP}; 判为new：第10章印刷页294称Guarienti领导下的Dresden Gallery，第14章印刷页350明确称Algarotti为Augustus of Saxony正在形成的同一绘画馆制定扩充与完成方案；两章身份锚点相合。"
        "该组指机构，不扩写为Augustus III个人绘画收藏或实体建筑；没有外部身份核验。"
    )
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    pending = planned_by_id[PENDING_CID]
    pending["decision"] = "undecided"
    pending["ku_id"] = ""
    pending["resolution_note"] = (
        "source_ref=candidate_ref=chp-14:14_CHP-14_intro:l3-12#L7; mentions="
        "m-s2-ch14-p347-006,m-chp14-p355-0037,m-chp14-p355-0043; "
        "prior_decision=new; prior_group_id=sg3-institution-dresden-gallery; "
        "prior_rationale=the p.347 Dresden royal-gallery mention was grouped with the Guarienti Dresden Gallery; "
        "current_decision=undecided because this candidate also maps the p.355 phrase 'royal collection' alongside 'gallery', "
        "so candidate-level alignment cannot safely map only the institution referent. Preserve the distinction between gallery and collection; "
        "revisit after mention/candidate scope is separated. No KU assigned."
    )

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "institution",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(values[key] for values in stats.values()) for key in next(iter(stats.values()))}
    new_result = sync.update_result(existing_result, stats, totals, len(planned_manifest)).rstrip()
    new_result += (
        "\n\n### institution：Dresden Gallery 跨章裁决与S4登记（2026-10-17）\n\n"
        f"`{CID}` 依据第10章 p.294 与第14章 p.350 映射至[德累斯顿绘画馆卡](../units/institutions/dresden-gallery.md)；3条直接关系候选留待S6。"
        f"`{PENDING_CID}` 改列 `undecided`：同一候选还映射到第14章 p.355 的“royal collection”，当前粒度不能安全地只对齐画廊机构；未分配KU，待拆清提及范围。"
        "不把个人收藏、具体画作或实体建筑并入绘画馆。\n\n"
        f"全书S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    new_process = existing_process.rstrip() + (
        f"\n\n<a id=\"{S3_ANCHOR}\"></a>\n\n"
        "### S3 institution：Dresden Gallery 与 royal collection 候选范围拆分（2026-10-17）\n\n"
        f"复核既有跨章组后，`{CID}` 保持 `new` 组 `{GROUP}`：第10章印刷页294（Markdown L298–299）明确称 Guarienti 领导下的 Dresden Gallery；第14章印刷页350（L39）称 Algarotti 为 Augustus of Saxony 正在形成的画廊制定扩充与完成计划，两个锚点指向同一绘画馆机构。此组不等同于 Augustus III 的个人绘画收藏或某座实体建筑。\n\n"
        f"`{PENDING_CID}` 从原 `{GROUP}` 组改列 `undecided`。其第14章候选除 p.347 L7 的 “royal gallery at Dresden” 外，还把 p.355 “royal collection” 词组和另一处 “gallery” 一并映射为同一候选。S3 按候选粒度对齐，现不能只将画廊提及映射至机构KU；暂不合并、不新建收藏KU，待 mention/candidate scope 分离后再裁决。对齐行保留原分组及变更理由。\n\n"
        f"<a id=\"{S4_ANCHOR}\"></a>\n\n"
        "### S4 institution：Dresden Gallery 登记（2026-10-17）\n\n"
        f"`{CID}` 登记为一个 institution KU：[Dresden Gallery](../../../{CARD_REL})。卡片只采用第10章 p.294 和第14章 p.350 的机构锚点，保留 Guarienti 与 Algarotti 的关系候选及方案未必实施的限定。`{PENDING_CID}` 不映射该卡。3条直接S2关系候选留待S6：{', '.join(f'`{sid}`' for sid in RELATION_IDS)}。没有新增正式关系或外部身份断言。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    new_accepted = add_accepted_path(accepted_text)
    new_card = make_card()

    if args.dry_run:
        print(f"S3: {CID} -> new institution group {GROUP}; {PENDING_CID} -> undecided pending mention/candidate scope split.")
        print(f"S4: add {KU_ID} ({CARD_REL}); {len(actual_relations)} relation candidates remain for S6.")
        print(f"Counts: new={totals['new_candidates']} candidates/{totals['new_groups']} groups; undecided={totals['undecided']}; "
              f"registered groups={totals['registered_groups']}, members={totals['registered_members']}, "
              f"pending groups={totals['pending_groups']}, members={totals['pending_members']}, KU={len(planned_manifest)}.")
        print("Planned files: alignment.csv, ku-manifest.csv, accepted.yml, institution card, process/knowledge.md, result.")
        print("\n--- Reviewable diff ---")
        show_diff("04-knowledge/tables/alignment.csv", render_csv(alignment_fields, alignments), render_csv(alignment_fields, planned_alignments))
        show_diff("04-knowledge/tables/ku-manifest.csv", render_csv(manifest_fields, manifest), render_csv(manifest_fields, planned_manifest))
        show_diff("04-knowledge/accepted.yml", accepted_text, new_accepted)
        show_diff(CARD_REL, "", new_card)
        show_diff("03-processing/patrons-and-painters-full-book-s2/process/knowledge.md", existing_process, new_process)
        show_diff("04-knowledge/results/patrons-and-painters-full-book-s2.md", existing_result, new_result)
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_text(ACCEPTED_PATH, new_accepted)
    write_text(CARD_PATH, new_card)
    write_text(PROCESS_PATH, new_process)
    write_text(RESULT_PATH, new_result)
    print(f"APPLIED: {CID} -> {KU_ID}; {PENDING_CID} remains undecided; {len(actual_relations)} relation candidates pending S6.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
