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
CANDIDATE = "cand-7618"
GROUP = "archive-group-c1033ea3e250"
KU_ID = "units/archives/monaco-raccolta-112-stampe-1763"
NAME_ZH = "圣史绘画112幅版画集（1763年版）"
NAME_EN = "Collection of 112 Prints of Sacred-History Paintings (1763 edition)"
ITALIAN_TITLE = (
    "Raccolta di centododici stampe di pittura della storia sacra incise per la prima volta in rame, "
    "e fedelmente copiate dagli originali esistenti in Venezia di celebri autori antichi e moderni"
)
CARD_REL = f"04-knowledge/{KU_ID}.md"
CHP8_FILE = "02-sources/02-Markdown/08_CHP-8_sec_i_notes_p214_visual-transcription.md"
CHP13_FILE = "02-sources/02-Markdown/13_CHP-13_intro.md"
BIB_FILE = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
RELATION_IDS = {
    "st-chp13-p345-monaco-1763-later-edition",
    "st-chp13-p345-monaco-collection-advertised-dealer",
    "st-chp13-p345-monaco-pittoni-works-reproduced",
    "st-chp13-p345-monaco-three-works-reproduced",
    "st-chp13-p345-monaco-tiepolo-works-reproduced",
}
ANCHOR = "s4-archive-monaco-raccolta-112-1763-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
TRECCANI_URL = "https://www.treccani.it/enciclopedia/pietro-monaco_(Dizionario-Biografico)/"
LOMBARDIA_URL = "https://www.lombardiabeniculturali.it/stampe/schede/H0540-05143/"


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
        "sub_type": "illustrated print publication",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第21章书目，印刷页430；OCR L830",
                "sentence_summary": "书目以 Pietro Monaco 为责任者，列出《Raccolta di centododici stampe di pittura della storia sacra…》并记 Venice 1763；这是本卡所指版次的主要书内书目锚点。",
                "original_quotes": [
                    {
                        "source_span": "line 830; bibliography print p.430",
                        "text": f"Monaco, Pietro: {ITALIAN_TITLE}, Venezia 1763.",
                    },
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": BIB_FILE,
                    "source_span": "line 830; bibliography print p.430",
                },
            },
            {
                "citation": BOOK_CITATION,
                "location": "第8章 p.214 注4；视觉转录 OCR L4；第13章 p.345，OCR L165–167、注1 L249",
                "sentence_summary": "第8章注4定位 Pietro Monaco 1763 年版画集中的第42、51、89号版画。第13章称该系列始于1743年，1763年及之后另有版次，增至112幅；注1给出无年份的短题名，不能据此判定其对应1763年版或后出版本。",
                "original_quotes": [
                    {"source_span": "line 4; print p.214, note 4", "text": "the engravings of Pietro Monaco published in 1763, Nos. 42, 51 and 89"},
                    {"source_span": "lines 165–166; print p.345", "text": "Later editions in 1763 and then in 1779"},
                    {"source_span": "line 167; print p.345", "text": "eight drawings by Tiepolo, nine paintings by Pittoni"},
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": CHP8_FILE,
                    "source_span": "chp-8:08_CHP-8_sec_i_notes_p214_visual-transcription:l1-4#L4; see also chp-13:13_CHP-13_intro:l161-171#L165-L167 and note 1",
                },
            },
            {
                "citation": "Laura Orbicciani, “MONACO, Pietro,” *Dizionario Biografico degli Italiani*, vol. 75 (2011). "
                + TRECCANI_URL
                + " Accessed 2026-10-17.",
                "location": "edition-history paragraphs describing the 1763 definitive edition and later republications",
                "sentence_summary": "Treccani identifies the 1763 publication as the definitive edition and reports later republications in 1772 and 1789. This supports the distinction between the 1763 publication and later editions; its 1789 Viero date differs from Haskell's 1779 date and does not resolve that discrepancy.",
                "original_quotes": [
                    {"source_span": "edition-history paragraphs", "text": "Nel 1763 pubblicò la definitiva edizione"},
                    {"source_span": "edition-history paragraphs", "text": "nel 1772"},
                    {"source_span": "edition-history paragraphs", "text": "nel 1789 una nuova edizione"},
                ],
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }, allow_unicode=True, sort_keys=False, width=1000)
    chp8_link = "[第8章 p.214 注4](../../../02-sources/02-Markdown/08_CHP-8_sec_i_notes_p214_visual-transcription.md)"
    chp13_link = "[第13章 p.345](../../../02-sources/02-Markdown/13_CHP-13_intro.md)"
    bib_link = "[第21章书目 p.430](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)"
    relation_text = ", ".join(sorted(RELATION_IDS))
    return f"""---
{fm}---

## 内容

### 题名与版本

- **中文描述性题名：**《{NAME_ZH}》；这是据原题形成的工作译名，不声称为正式中译题名。
- **原题：** *{ITALIAN_TITLE}*。Haskell 第21章书目将其列为 Pietro Monaco 的 Venice 1763 出版物；此处以该书目身份登记出版版次。
- **文献类型：**有插图和版画内容的出版物，按 archive 登记。112幅具体版画作为出版物内容，不与出版载体合并为另一个同名 KU。

### 内容与涉及对象

**中文：** Haskell 第8章 p.214 注4以第42、51、89号版画为定位，指向 Pietro Monaco 1763 年出版的版画集；第13章 p.345 称 Monaco 的版画系列由1743年的55幅扩展，后续版次增至112幅，并列出 Tiepolo 的8幅素描、Pittoni 的9幅绘画以及 Zais、Piazzetta、Nazari 各一件。该页称 Monaco “几乎可以肯定”借版画宣传其经销活动，此为 Haskell 的解释。个别版画和原画保持为各自的 work 对象；本卡记录出版版次，不声称已查阅实物。〔{chp8_link}；{chp13_link}；{bib_link}〕

**English:** Chapter 8, p.214, note 4, locates engravings nos. 42, 51, and 89 in Pietro Monaco’s 1763 publication. Chapter 13, p.345, says Monaco’s print series grew from the 1743 collection of 55 prints to later editions with 112 plates; it lists eight Tiepolo drawings, nine Pittoni paintings, and one each by Zais, Piazzetta, and Nazari. Haskell says Monaco was “almost certainly” using the plates to advertise his dealer activity; this remains Haskell’s interpretation. Individual prints and the paintings they reproduce remain distinct work objects. This card records the publication edition; the volume and plates were not independently inspected. ({chp8_link}; {chp13_link}; {bib_link})

### 版次边界与待证差异

- Haskell 第13章将1743年 collection、1763年后续版及再后来的版次分开；第21章书目明确为本卡的完整题名与1763年出版项。第13章注1只有短题名、没有年份，故不据该注把题名强配到1763或其他版次。
- Haskell 称 Viero 后出版次为1779年；Treccani《意大利人传记辞典》称系列1763年出定本、1772年由 Alessandri 与 Scattaglia 重印，并称1789年有 Teodoro Viero 新版。后出版本年代差异仍待证，本卡只登记书目直接支持的1763年版，不改写独立版次候选。
- Treccani 记录版画系列的出版沿革；Lombardia Beni Culturali 的相关记录指向该系列中的具体版画，粒度不同，未作为本版次的同一外部标识写入 alignment.csv。

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。五条直接 S2 候选（{relation_text}）留待 S6；作品名单的分组不等于对每幅版画或原画的识别。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Pietro Monaco's 1763 112-print publication as an S4 archive.")
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
    assert candidate["canonical_name"].startswith("Raccolta di centododici stampe")
    assert candidate["candidate_source_ref"] == "chp-8:08_CHP-8_sec_i_notes_p214_visual-transcription:l1-4#L4"
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
    assert any(
        row.get("statement_id") == "st-chp21-bib-l808-844-entry-15"
        and row.get("object_candidate_id") == CANDIDATE
        and (row.get("qualifiers") or {}).get("bibliographic_record", {}).get("publication_details_as_printed") == "Venezia 1763"
        for row in statements
    )
    # The 1779/1789 discrepancy is recorded as unresolved; do not merge or rewrite the later-edition candidate.
    assert any(row.get("candidate_id") == "cand-10116" for row in candidates)

    planned_alignments = [dict(row) for row in alignments]
    changed = next(row for row in planned_alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    changed["ku_id"] = KU_ID
    changed["process_ref"] = PROCESS_REF
    changed["resolution_note"] += (
        f" S4登记（{DATE}）：{GROUP} 映射至 {KU_ID}；按 Haskell 第21章书目登记1763年出版版次。"
        "版画作为出版物内容与出版载体分开；不合并1743、后出版本或个别版画。"
        "Treccani 报告1772及1789年后出版本，与 Haskell 的1779年 Viero 日期存在待证差异；五条关系候选仍留待 S6。"
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
    assert totals["registered_groups"] == 680
    assert totals["registered_members"] == 841
    assert totals["pending_groups"] == 4105
    assert totals["pending_members"] == 4127

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 archive：Pietro Monaco 1763 年版画集登记（{DATE}）\n\n"
        f"{CANDIDATE} 保持单成员 new 组 {GROUP}，登记为[《{NAME_ZH}》（{NAME_EN}）](../../../{CARD_REL})（{KU_ID}）。"
        "本卡指第21章书目明确列出的完整 Venice 1763 版次；版画作为出版物内容，逐件作品另有 work 身份。"
        "第13章注1无年份，不将其短题名强配到1763或其他版次。\n"
        "类型与版次核对参照 Treccani《意大利人传记辞典》Pietro Monaco 条目（2011，edition-history paragraphs，访问2026-10-17；"
        f"{TRECCANI_URL}）：该文称1763年为定本，后续版次为1772、1789。Haskell p.345 将 Viero 后出版记为1779；年代差异保留待证。"
        "Lombardia Beni Culturali 相关页面记录的是该系列中的具体版画，不作为整版的同粒度外部身份标识。"
        f"（{LOMBARDIA_URL}）\n"
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
        f"\n\n### S3/S4 archive：Pietro Monaco 1763 年版画集登记（{DATE}）\n\n"
        f"{CANDIDATE} → [《{NAME_ZH}》（{NAME_EN}）](../units/archives/monaco-raccolta-112-stampe-1763.md)；"
        "Haskell 与 Treccani 对后出 Viero 版的年份不同，保留待证。"
    )

    assert len(planned_manifest) == len(manifest) + 1
    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE} {GROUP}->{KU_ID}; members={members}; relation_candidates={len(direct)}; "
            f"version_conflict=Haskell:1779/Treccani:1789; manifest={len(manifest)}->{len(planned_manifest)}; "
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
