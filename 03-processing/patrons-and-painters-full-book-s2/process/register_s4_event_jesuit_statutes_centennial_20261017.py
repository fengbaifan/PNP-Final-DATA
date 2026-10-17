from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_i.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CANDIDATE = "cand-4981"
GROUP = "sg3-event-cand-4981"
KU_ID = "units/events/jesuit-statutes-centenary-celebrations-1639-1640"
CARD_REL = f"04-knowledge/{KU_ID}.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "耶稣会会规获批百周年庆祝（1639–1640）"
NAME_EN = "Jesuit Statutes Centenary Celebrations (1639–1640)"
ANCHOR = "s4-event-jesuit-statutes-centenary-1639-1640-20261017"
QUOTE = (
    "In 1639 and 1640 he paid two visits to their church, the Gesù, "
    "during the celebrations to mark the centenary of the approval of their statutes"
)


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "event",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": f"{BOOK_CITATION}, ch. 3, p. 64.",
                "location": "第3章，印刷页64；OCR L18。",
                "sentence_summary": (
                    "Haskell称 Urban VIII 于1639和1640年两次到访耶稣堂，"
                    "当时正在庆祝耶稣会会规获批一百周年。"
                ),
                "original_quotes": [
                    {
                        "source_span": "OCR line 18; print p. 64",
                        "text": QUOTE,
                    }
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": "OCR line 18; printed p. 64",
                },
            }
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = "[第3章 p.64](../../../02-sources/02-Markdown/03_CHP-3_sec_i.md#L18)"
    urban_link = "[Urban VIII](../persons/urbano-viii.md)"
    gesu_link = "[耶稣堂](../places/gesu-rome.md)"
    return f"""---
{fm}---

## 内容

### 事件身份与范围

**中文：** 本卡记录哈斯克尔所述、围绕耶稣会会规获批百周年举行的庆祝语境。作者称 {urban_link} 于1639和1640年两次到访 {gesu_link}，当时正在举行百周年庆祝。两次到访是原文给出的具体活动；本卡不将庆祝语境压缩成单次接待，也不计算会规批准的具体日期。{source_link}（L18）

**English:** This unit records the centenary celebration context described by Haskell for the approval of the Jesuit statutes. He says {urban_link} visited the Gesù twice, in 1639 and 1640, while the centenary was being celebrated. The two visits are the specific activities named in the source; this card does not reduce the celebration context to a single reception or calculate the original approval date. {source_link} (L18)

### 事件信息

- **事件性质：** 耶稣会会规获批百周年庆祝语境；对应两次到访，不拆成两个身份对象。{source_link}（L18）
- **时间：** Urban VIII 的两次到访分别发生于1639年和1640年；庆祝活动整体起止日期未载。{source_link}（L18）
- **地点：** {gesu_link}；此处指被到访的教堂，不补写其他庆祝地点。{source_link}（L18）
- **来源提及人物：** {urban_link}，以访客身份出现；本卡链接用于身份导航，不等同于正式关系记录。{source_link}（L18）

### 对象边界

与第2章 cand-4761 的1639年接待候选分开：两者同属会规获批百周年语境，但本卡对应哈斯克尔所述的两次 Urban VIII 到访，未据共同节庆背景合并身份。

## 关系与证据

当前没有已登记的正式关系。S2 的 book-statements.jsonl 当前没有绑定 cand-4981 的关系候选；上文人物与地点链接只作身份导航，不构成正式边。未新增 S5 enrichment。
"""


def insert_accepted_path(text: str) -> str:
    lines = text.splitlines()
    assert f"- {CARD_REL}" not in lines
    insert_at = next(
        (
            i for i, line in enumerate(lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL
        ),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Jesuit statutes centenary celebration context in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    candidate = candidate_map[CANDIDATE]
    target = decisions[CANDIDATE]
    assert candidate.get("suggested_type") == "event"
    alignment_group = sync.get_group(target.get("resolution_note", ""))
    assert alignment_group == GROUP
    assert target.get("decision") == "new" and not target.get("ku_id")
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert candidate.get("candidate_source_ref", "").endswith("#L18")
    assert not CARD_PATH.exists()
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "event" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "same English event identity already exists"

    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    assert " ".join(QUOTE.split()) in source_text
    assert decisions["cand-4761"].get("decision") in {"same", "new", "undecided", "conflict", "excluded"}
    assert (ROOT / "04-knowledge/units/persons/urbano-viii.md").exists()
    assert (ROOT / "04-knowledge/units/places/gesu-rome.md").exists()
    statements = sync.load_statements()
    assert not any(
        CANDIDATE in {
            row.get("subject_candidate_id"), row.get("object_candidate_id"),
            *row.get("qualifiers", {}).get("mentioned_candidate_ids", []),
        }
        for row in statements
    ), "cand-4981 has acquired a direct S2 statement; inspect before registration"

    planned_alignment = [dict(row) for row in alignments]
    mapped = [row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source")]
    assert len(mapped) == 1
    mapped[0]["ku_id"] = KU_ID
    mapped[0]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    mapped[0]["resolution_note"] += (
        f" S4 registration: source-backed event group {GROUP} maps to {KU_ID}; "
        "the two visits are preserved as a collective centenary context, distinct from the separate 1639 reception candidate cand-4761."
    )

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "event",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip()
    process_text += f"""

<a id="{ANCHOR}"></a>

### S4 event：耶稣会会规获批百周年庆祝语境（{DATE}）

单成员 S3 事件组 {GROUP}（{CANDIDATE}）登记至[百周年庆祝事件卡](../../../04-knowledge/{KU_ID}.md)。第3章 p.64 称 Urban VIII 于1639和1640年两次到访耶稣堂，当时正在庆祝耶稣会会规获批百周年。本卡将这两次到访保留为共同庆祝语境，不拆成两项，也不推算会规批准日。

该对象与第2章 1639 年接待候选 cand-4761 保持分立：两者处于同一百周年纪念语境，但当前 S3 决定分别对应两次到访的集体语境与单次接待。来源行未为 cand-4981 生成 book-statements 关系候选；本次只登记事件身份，不新增正式关系，不能据此宣称其关系审查已完成。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    result_text = result_text.rstrip() + (
        f"\n\n### S4 event：耶稣会会规获批百周年庆祝语境（{DATE}）\n\n"
        "单成员事件组 cand-4981 登记为 source-backed KU，记录 Urban VIII 于1639、1640年两次到访耶稣堂的共同庆祝语境；"
        "与第2章 cand-4761 的1639年接待保持分立。S2 未绑定该候选的关系记录，本次不新增正式关系或 S5 补足。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。\n"
    )
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print(f"dry-run passed: {CANDIDATE} is the complete single-member S3 event group {GROUP}")
        print("source quotation verified; Urban VIII and the Gesù identity cards exist")
        print("separate 1639 reception candidate cand-4761 retained; no S2 relation candidate attached to cand-4981")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; accepted path unique")
        print("planned writes: one bilingual event card, accepted.yml, ku-manifest.csv, one alignment mapping, process record, result")
        return 0

    CARD_PATH.write_text(card_content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text.rstrip() + "\n", encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

