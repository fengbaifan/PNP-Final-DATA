from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
CANDIDATE = "cand-6390"
GROUP = "archive-group-7156a2e4e186"
KU_ID = "units/archives/the-table-pinax-dialogue"
NAME_ZH = "寓意人生图的对话"
NAME_EN = "The Table (Pinax dialogue)"
CARD_REL = f"04-knowledge/{KU_ID}.md"
BODY_FILE = "02-sources/02-Markdown/06_CHP-6_sec_iv.md"
RELATION_IDS = {
    "st-chp6-p157-effetti-literary-interest",
    "st-chp6-p157-renaissance-ekphrasis",
    "st-chp6-p157-table-attribution-correction",
    "st-chp6-p157-table-content",
    "st-chp6-p157-table-vogue-mascardi",
}
ANCHOR = "s4-archive-the-table-pinax-dialogue-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def insert_accepted(lines: list[str]) -> list[str]:
    entry = f"- {CARD_REL}"
    assert entry not in lines
    units_idx = lines.index("units:")
    claims_idx = next(
        (i for i in range(units_idx + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])),
        len(lines),
    )
    insert_at = next(
        (i for i in range(units_idx + 1, claims_idx) if lines[i].startswith("- ") and lines[i][2:] > CARD_REL),
        claims_idx,
    )
    lines.insert(insert_at, entry)
    return lines


def make_card() -> str:
    fm = yaml.safe_dump({
        "title": f"《{NAME_ZH}》（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "ancient philosophical dialogue",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第6章，印刷页157；正文及注2 OCR L55–72、续注 L7–10",
                "sentence_summary": "Haskell 正文称一篇对话为 The Table，注2称 Pinax，并纠正作者归属且给出可能年代。正文转述作品内容，并记 Mascardi 于1629年翻译兼作长篇评注；续注说明 Haskell 使用 H. E. Seebohm 于1906年提供的英文版本。均为 Haskell 的书内报告，所述文献版本未独立查阅。",
                "original_quotes": [
                    {"source_span": "line 56; print p.157", "text": "called The Table"},
                    {"source_span": "line 58; print p.157, note 2", "text": "the Pinax is by a totally different author"},
                    {"source_span": "line 58; print p.157, note 2", "text": "probably dates from the first century A.D."},
                    {"source_span": "line 10; continuation of note 2, print p.157", "text": "English version by H. E. Seebohm"},
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": BODY_FILE,
                    "source_span": "chp-6:06_CHP-6_sec_iv:l55-72#L56,L58 and l7-10#L10; print p.157",
                },
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }, allow_unicode=True, sort_keys=False, width=1000)
    body_link = "[第6章 p.157](../../../02-sources/02-Markdown/06_CHP-6_sec_iv.md)"
    relation_text = ", ".join(sorted(RELATION_IDS))
    return f"""---
{fm}---

## 内容

### 题名与文献类型

- **中文描述性题名：**《{NAME_ZH}》；这是据作品内容形成的工作译名，不声称为正式中译题名。
- **Haskell 所用题名：** 正文称 *The Table*，同页注2称 *Pinax*。同一脚注直接校正正文所述归属，故本卡将二者作为该对话的题名形式记录。
- **文献类型：** Haskell 称其为柏拉图式对话；按本项目文献总类登记为 archive。

### 内容概要

**中文：** Haskell 转述该对话描述一幅象征人生的图像：两名旅人于 Kronos 神庙前发现它，由一名陌生人解释其中的恶习、虚假价值与美德回报。图像是对话内部所述内容，本卡登记的是对话文本，不将该图像另立为 work。Haskell 评价其形式和内容均少有原创性；这是作者评价，不作客观属性。本卡内容限于第6章 p.157 的书内转述。〔{body_link}〕

**English:** Haskell summarizes the dialogue as describing an allegorical picture of human life found by two travellers before a temple of Kronos; a stranger explains vice, false values, and the rewards of virtue. The picture belongs to the dialogue’s narrative and is not registered here as a separate work. Haskell judges the dialogue to show little originality in form or content; this remains his evaluation, not an objective attribute. This description is limited to the book’s account on chapter 6, p.157. ({body_link})

### 作者、年代与版本

- Haskell 说正文写作时该对话被归于 Cebes；注2明确否定这一归属，称作者另有其人但未具名，并谨慎称其“可能”作于公元一世纪。不得将 Cebes 登记为本对话作者。
- Haskell 称 Agostino Mascardi 于1629年翻译并作长篇评注，认为该译本推动了作品流行；这些均是 Haskell 的书内报告。
- 注2续文称 Haskell 使用 H. E. Seebohm 于1906年提供的英文版本。该版本的确切题名和出版者未在此处给出，单独候选 cand-6407 保持 undecided；本 archive KU 指向被讨论的对话，不与该英译版本合并。所引译本未独立查阅。

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。直接 S2 候选（{relation_text}）留待 S6；Cebes、Socrates、Kronos 相关的归属、叙事角色及类型边界不据此转成新的身份事实。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register The Table / Pinax as a source-backed S4 archive.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE)
    decision = next(row for row in alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    assert candidate["suggested_type"] == "archive"
    assert candidate["canonical_name"].startswith("The Table (Pinax;")
    assert candidate["candidate_source_ref"] == "chp-6:06_CHP-6_sec_iv:l55-72#L56"
    assert decision["decision"] == "new" and not decision.get("ku_id")
    assert sync.get_group(decision.get("resolution_note", "")) == GROUP
    members = [
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert members == [CANDIDATE]
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not any(
        row.get("type") == "archive" and "pinax" in row.get("name_en", "").casefold()
        for row in manifest
    )
    assert not (ROOT / CARD_REL).exists()
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    assert CARD_REL not in accepted_lines

    body = (ROOT / BODY_FILE).read_text(encoding="utf-8-sig")
    assert "a Platonic dialogue called The Table" in body
    assert "the Pinax is by a totally different author" in body
    assert "probably dates from the first century" in body
    assert "English version by H. E. Seebohm" in body
    assert not any(
        row.get("candidate_id") == "cand-6407" and row.get("decision") == "new" and row.get("ku_id")
        for row in alignments
    )
    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = {
        row["statement_id"] for row in statements
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and CANDIDATE in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    }
    assert direct == RELATION_IDS

    planned_alignments = [dict(row) for row in alignments]
    changed = next(row for row in planned_alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    changed["ku_id"] = KU_ID
    changed["process_ref"] = PROCESS_REF
    changed["resolution_note"] += (
        f" S4登记（{DATE}）：{GROUP} 映射至 {KU_ID}；登记 The Table / Pinax 对话为书内来源限定 archive KU。"
        "正文题名与注2明确相连；作者仅知为不同于Cebes的未具名作者，年代仍为可能公元一世纪。"
        "英译本候选 cand-6407 仍 undecided，不合并；五条直接 S2 关系候选留待 S6。"
    )
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = insert_accepted(accepted_lines)
    card = make_card()
    fm_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert fm_match and isinstance(yaml.safe_load(fm_match.group(1)), dict)

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["same_candidates"] == 1891
    assert totals["new_candidates"] == 4968
    assert totals["new_groups"] == 4785
    assert totals["registered_groups"] == 679
    assert totals["registered_members"] == 840
    assert totals["pending_groups"] == 4106
    assert totals["pending_members"] == 4128

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 archive：The Table / Pinax 对话登记（{DATE}）\n\n"
        f"{CANDIDATE} 保持单成员 new 组 {GROUP}，登记为[《{NAME_ZH}》（{NAME_EN}）](../../../{CARD_REL})（{KU_ID}）。"
        "第6章 p.157 正文称 The Table，注2称 Pinax 并校正 Cebes 归属；同注仅称作者另有其人、可能作于公元一世纪。"
        "作品内部的寓意图不另立 work。Haskell 所用 Seebohm 英译本 cand-6407 仍为 undecided；不与古代对话合并。\n"
        f"- 五条直接 S2 候选 {', '.join(sorted(RELATION_IDS))} 留待 S6；未新增 formal relations。\n"
        f"- S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text, count = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>",
        result_text,
        count=1,
    )
    assert count == 1
    result_text += (
        f"\n\n### S3/S4 archive：The Table / Pinax 对话登记（{DATE}）\n\n"
        f"{CANDIDATE} → [《{NAME_ZH}》（{NAME_EN}）](../units/archives/the-table-pinax-dialogue.md)；"
        "作者未具名、年代保留 probably 限定，Seebohm 英译本保持独立待决。"
    )

    assert len(planned_manifest) == len(manifest) + 1
    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE} {GROUP}->{KU_ID}; relation_candidates={len(direct)}; "
            f"separate_version=cand-6407:undecided; manifest={len(manifest)}->{len(planned_manifest)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}"
        )
        return 0

    (ROOT / CARD_REL).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE}->{KU_ID}; manifest={len(planned_manifest)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
