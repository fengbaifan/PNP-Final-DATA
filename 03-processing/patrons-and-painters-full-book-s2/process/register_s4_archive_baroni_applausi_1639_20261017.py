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
CANDIDATE = "cand-5531"
GROUP = "archive-group-6e104b1ffa20"
KU_ID = "units/archives/applausi-poetici-leonora-baroni-1639"
NAME_ZH = "莱奥诺拉·巴罗尼颂诗集（1639年）"
NAME_EN = "Poetic Tributes to Leonora Baroni (1639 edition)"
ORIGINAL_TITLE = "Applausi poetici alle glorie della Sig.a Leonora Baroni"
CARD_REL = f"04-knowledge/{KU_ID}.md"
BODY_FILE = "02-sources/02-Markdown/04_CHP-4_sec_i.md"
RELATION_IDS = {
    "st-chp4-sec-i-l20-24-baroni-poems",
    "st-chp4-sec-i-l42-67-fn96-baroni-publication",
    "st-chp4-sec-i-l20-24-poems-by-admirers",
    "st-chp4-sec-i-l20-24-collection-honours-baroni",
}
ANCHOR = "s4-archive-applausi-poetici-baroni-1639-20261017"
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
        "sub_type": "poetry collection",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第4章，印刷页96；正文 OCR L21–22；注3 OCR L47",
                "sentence_summary": "Haskell 称 Paolo Giordano II 负责刊印数位赞颂 Leonora Baroni 的 admirers 所作诗歌；注3给出诗集题名、Bracciano 与1639年。S0 OCR 读作 plorie，过程记录所核扫描印本为 glorie；不改写来源文本。所引诗集未独立查阅。",
                "original_quotes": [
                    {
                        "source_span": "lines 21–22; print p.96",
                        "text": "he was responsible for publishing the poems written by a number of admirers in honour of Leonora Baroni",
                    },
                    {
                        "source_span": "line 47; print p.96, note 3 (scan reading)",
                        "text": "Applausi poetici alle glorie della Sig.a Leonora Baroni, Bracciano 1639.",
                    },
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": BODY_FILE,
                    "source_span": "chp-4:04_CHP-4_sec_i:l20-24#L21-L22 and l42-67#L47; print p.96",
                },
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }, allow_unicode=True, sort_keys=False, width=1000)
    source_link = "[第4章 p.96](../../../02-sources/02-Markdown/04_CHP-4_sec_i.md)"
    relation_text = ", ".join(sorted(RELATION_IDS))
    return f"""---
{fm}---

## 内容

### 题名与文献类型

- **中文描述性题名：**《{NAME_ZH}》；这是对应意大利原题的工作译名。
- **原题：** *{ORIGINAL_TITLE}*。注3印本读作 “glorie”；S0 OCR 读作 “plorie”。此处按扫描读数保存题名，S0 来源文件保持原样。
- **文献类型：**刊印的诗歌合集，按 archive 登记；诗篇未逐首具名，不拆建单首作品。

### 内容与责任

**中文：** Haskell 第4章 p.96 称 Paolo Giordano II 负责出版多位 admirers 为歌者 Leonora Baroni 所作的诗，并在注3将诗集题为 *Applausi poetici alle glorie della Sig.a Leonora Baroni*，注明 Bracciano、1639年。诗集未独立查阅；“负责出版”按 Haskell 的书内表述保留，作者群体未具名。〔{source_link}〕

**English:** Chapter 4, p.96, says Paolo Giordano II was responsible for publishing poems by several admirers in honour of the singer Leonora Baroni. Note 3 identifies the collection as *Applausi poetici alle glorie della Sig.a Leonora Baroni*, Bracciano, 1639. The collection was not independently consulted; “responsible for publishing” is retained as Haskell’s wording, and the contributing admirers are not named. ({source_link})

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。四条直接 S2 候选（{relation_text}）留待 S6；本卡只登记诗集及书内书目报告。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the 1639 Applausi poetici collection as an S4 archive.")
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
    assert candidate["canonical_name"] == "Applausi poetici alle glorie della Sig.a Leonora Baroni (Bracciano, 1639)"
    assert candidate["candidate_source_ref"] == "chp-4:04_CHP-4_sec_i:l20-24#L21"
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
        row.get("type") == "archive" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    )
    assert not (ROOT / CARD_REL).exists()
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    assert CARD_REL not in accepted_lines

    body = (ROOT / BODY_FILE).read_text(encoding="utf-8-sig")
    assert "he was responsible for publishing the poems written by a number of admirers" in body
    assert "Applausi poetici alle plorie della Sig. a Leonora Baroni, Bracciano 1639." in body
    stages = (ROOT / "03-processing" / TASK / "process" / "stages.md").read_text(encoding="utf-8-sig")
    assert "`plorie`→印本`glorie`" in stages
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
        f" S4登记（{DATE}）：{GROUP} 映射至 {KU_ID}；登记1639年刊印的 Baroni 颂诗集。"
        "题名按扫描读数 glorie 记录，S0 OCR plorie 保持不变；四条直接关系候选仍待 S6。"
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
    assert totals["registered_groups"] == 681
    assert totals["registered_members"] == 842
    assert totals["pending_groups"] == 4104
    assert totals["pending_members"] == 4126

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 archive：Applausi poetici 1639 年版登记（{DATE}）\n\n"
        f"{CANDIDATE} 保持单成员 new 组 {GROUP}，登记为[《{NAME_ZH}》（{NAME_EN}）](../../../{CARD_REL})（{KU_ID}）。"
        "正文称 Paolo Giordano II 负责出版赞颂 Leonora Baroni 的诗，注3给出题名、Bracciano 与1639年。"
        "S0 OCR `plorie` 与扫描印本 `glorie` 的校正依既有 stages.md 记录；S0 不改写。\n"
        f"- 四条直接 S2 候选 {', '.join(sorted(RELATION_IDS))} 留待 S6；未新增 formal relations。\n"
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
        f"\n\n### S3/S4 archive：Applausi poetici 1639 年版登记（{DATE}）\n\n"
        f"{CANDIDATE} → [《{NAME_ZH}》（{NAME_EN}）](../units/archives/applausi-poetici-leonora-baroni-1639.md)；"
        "题名 scan correction 依现有 S0 记录，四条关系候选仍待 S6。"
    )

    assert len(planned_manifest) == len(manifest) + 1
    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE} {GROUP}->{KU_ID}; members={members}; relation_candidates={len(direct)}; "
            f"title_correction=S0:plorie/scan:glorie; manifest={len(manifest)}->{len(planned_manifest)}; "
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
