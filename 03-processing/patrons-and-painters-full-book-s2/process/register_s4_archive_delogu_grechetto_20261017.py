from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
import register_s4_archive_memmo_query_sheet_20261017 as process_sync

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
ENTITY = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
BOOK = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
CID = "cand-11312"
GROUP = "archive-group-2bb2d5388a18"
KU = "units/archives/giuseppe-delogu-g-b-castiglione-il-grechetto-1928"
CARD = "04-knowledge/units/archives/giuseppe-delogu-g-b-castiglione-il-grechetto-1928.md"
ANCHOR = "s4-archive-delogu-grechetto-1928-20261017"
DIRECT = {"st-chp1-secii-p21-n1-cites-delogu-1928-p40n9"}

def make_card():
    metadata = {
        "title": "G. B. 卡斯蒂廖内（称作“格雷切托”）（G. B. Castiglione Called “Il Grechetto”）",
        "name_en": "G. B. Castiglione Called “Il Grechetto”",
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK,
                "location": "第21章书目，印刷页420，条目28；S2 line 415",
                "sentence_summary": "Haskell书目列出 Giuseppe Delogu 的 G. B. Castiglione detto Il Grechetto，出版地 Bologna，出版年1928；扫描页校正 OCR 中 II 为 Il。",
                "original_quotes": [{"source_span": "S2 line 415; print p.420", "text": "Delogu, Giuseppe: G. B. Castiglione detto II Grechetto, Bologna 1928."}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md", "source_span": "line 415; print p.420, entry 28"},
            },
            {
                "citation": BOOK,
                "location": "第1章 p.21 注1；source segment lines 894–895; PDF physical p.20",
                "sentence_summary": "Haskell称未能追踪的一部喜剧在 Delogu 1928 年版第40页注9另有提及；Delogu 的书及该页注均未独立查阅。",
                "original_quotes": [{"source_span": "source segment lines 894–895; print p.21 n.1", "text": "This comedy, which I have unfortunately not been able to trace, is referred to in another connection by G. Delogu, 1928, p. 40, note 9."}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/01_CHP-1_sec_ii.md", "source_span": "lines 233–233; print p.21 n.1"},
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=1000)
    body = """## 内容

### 描述

**中文：** 本卡登记 Haskell 书目所列的 Giuseppe Delogu 专著。第21章书目载题名 G. B. Castiglione detto Il Grechetto、出版地 Bologna 和出版年1928；原 OCR 的 II 已按扫描页校正为 Il。第1章 p.21 注1指出，一部未能追踪的喜剧在该书 p.40 n.9 另有提及。Delogu 的书及该注未独立查阅，本卡只记录 Haskell 给出的书目信息和引用位置。中文题名为工作译名，原题名保留。

**English:** This unit records the monograph listed in Haskell’s bibliography under Giuseppe Delogu. Chapter 21 gives the title G. B. Castiglione detto Il Grechetto, publication place Bologna, and year 1928; the OCR reading “II” is corrected to “Il” against the page image. Chapter 1, p. 21 n. 1 says that an untraced comedy is also mentioned in that book at p. 40 n. 9. Neither the Delogu volume nor that cited note was independently consulted. This card records only Haskell’s bibliographic information and citation pointer. The Chinese title is a working translation; the original title is retained.

### 题名

| 字段 | 值 | 证据 |
|---|---|---|
| 中文工作题名 | G. B. 卡斯蒂廖内（称作“格雷切托”） | S1（第21章书目，印刷页420；工作译名） |
| 原题名 | G. B. Castiglione detto Il Grechetto | S1（第21章书目，印刷页420；S2据扫描页校正 OCR） |

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 文献类型 | 书籍（专著） | S1（第21章书目，印刷页420） |

### 责任者

| 字段 | 值 | 证据 |
|---|---|---|
| 作者（按书目著录） | Giuseppe Delogu | S1（第21章书目，印刷页420） |

### 出版

| 字段 | 值 | 证据 |
|---|---|---|
| 出版地 | Bologna | S1（第21章书目，印刷页420） |
| 出版年 | 1928 | S1（第21章书目，印刷页420） |

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。Haskell 第1章 p.21 注1对该书第40页注9的引用候选 st-chp1-secii-p21-n1-cites-delogu-1928-p40n9 留待 S6；被提及的 Delogu 内容未独立查阅，不据此预先建立正式引用边。逐组记录见[过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-archive-delogu-grechetto-1928-20261017)。
"""
    return f"---\n{fm}---\n\n{body}"

def insert_accepted(lines, card_path):
    units_idx = lines.index("units:")
    claims_idx = next((i for i in range(units_idx + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])), len(lines))
    entry = f"- {card_path}"
    assert entry not in lines
    at = next((i for i in range(units_idx + 1, claims_idx) if lines[i].startswith("- ") and lines[i][2:] > card_path), claims_idx)
    lines.insert(at, entry)
    return lines

def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    af, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    mf, manifest = sync.read_csv(MANIFEST)
    candidate = next(row for row in candidates if row["candidate_id"] == CID)
    matches = [r for r in alignments if r.get("candidate_id") == CID and not r.get("external_source")]
    assert len(matches) == 1
    alignment = matches[0]
    assert candidate["suggested_type"] == "archive" and candidate["candidate_source_ref"] == "chp-21:21_CHP-21Bibliography:l376-418#L415"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    members = [r["candidate_id"] for r in alignments if r.get("candidate_id") and not r.get("external_source") and r["decision"] == "new" and sync.get_group(r.get("resolution_note", "")) == GROUP]
    assert members == [CID]
    assert not any(r.get("ku_id") == KU for r in manifest)
    assert not (ROOT / CARD).exists()
    accepted = ACCEPTED.read_text(encoding="utf-8-sig").splitlines()
    assert f"- {CARD}" not in accepted

    statements = [json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    direct = {r["statement_id"] for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and CID in (r.get("subject_candidate_id"), r.get("object_candidate_id"))}
    assert direct == DIRECT
    bibliography = next(r for r in statements if r.get("statement_id") == "st-chp21-bib-l376-418-entry-28")
    corrections = (bibliography.get("qualifiers") or {}).get("page_image_ocr_corrections", [])
    assert any(c.get("ocr") == "II Grechetto" and c.get("print") == "Il Grechetto" for c in corrections)
    citation = next(r for r in statements if r.get("statement_id") == next(iter(DIRECT)))
    assert (citation.get("qualifiers") or {}).get("cited_material_not_independently_consulted") is True

    planned = [dict(r) for r in alignments]
    target = next(r for r in planned if r.get("alignment_id") == alignment["alignment_id"])
    target["ku_id"] = KU
    target["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    target["resolution_note"] += f" S4登记（{DATE}）：{GROUP} 映射至 {KU}；全书书目 p.420 entry 28 载作者、原题名、出版地及年份；p.21 n.1 的 Delogu p.40 n.9 引用仍待 S6。书及所引内容未独立查阅。"
    planned_manifest = sorted([*manifest, {"ku_id": KU, "type": "archive", "canonical_name": "G. B. 卡斯蒂廖内（称作“格雷切托”）", "name_en": "G. B. Castiglione Called “Il Grechetto”", "source_task": TASK, "card_path": CARD}], key=lambda row: row["ku_id"])
    planned_accepted = insert_accepted(accepted, CARD)
    card = make_card()
    header = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert header and isinstance(yaml.safe_load(header.group(1)), dict)

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(value[key] for value in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] == 697 and totals["registered_members"] == 858
    assert totals["pending_groups"] == 4087 and totals["pending_members"] == 4109
    assert len(planned_manifest) == len(manifest) + 1
    process_text = process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 archive：Delogu《G. B. Castiglione detto Il Grechetto》登记（{DATE}）\n\n"
        f"cand-11312（body-mention，source anchor 指向第21章书目 line 415）保持单成员 new 组 {GROUP}，登记为[G. B. 卡斯蒂廖内（称作“格雷切托”）](../../../{CARD})（{KU}）。"
        "Haskell书目印刷页420提供作者、原题名、Bologna和1928；S2据扫描页将 OCR 的 II 校为印刷题名 Il。第1章 p.21 n.1 引用该书 p.40 n.9，但 Delogu 专著及被引内容均未独立查阅。\n"
        f"- 直接关系候选 {', '.join(sorted(DIRECT))} 留待 S6；本卡不新增 formal relations。"
    )

    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text, n = re.subn(r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)", rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>", result_text, count=1)
    assert n == 1
    if args.dry_run:
        print(f"dry-run passed: {CID}->{KU}; direct_relation_candidates={len(direct)}; manifest={len(manifest)}->{len(planned_manifest)}; registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}")
        return 0
    (ROOT / CARD).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT, af, planned)
    sync.write_csv(MANIFEST, mf, planned_manifest)
    ACCEPTED.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: {CID}->{KU}; manifest={len(planned_manifest)}; registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
