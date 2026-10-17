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
CID = "cand-1060"
GROUP = "new-person:andrew-fountaine-7d5ace0041"
KU = "units/persons/andrew-fountaine"
CARD = "04-knowledge/units/persons/andrew-fountaine.md"
ANCHOR = "s4-person-andrew-fountaine-20261017"
DIRECT = {"st-chp10-p279-narford-seat-fountaine"}
RELATED = DIRECT | {"st-chp13-p343-notes-note3-named-dedicatees"}

def make_card():
    metadata = {
        "title": "安德鲁·方丹爵士（Sir Andrew Fountaine）",
        "name_en": "Sir Andrew Fountaine",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK,
                "location": "全书索引 F.csv#75；所列页码279、343n",
                "sentence_summary": "Haskell索引将第10章及第13章注释中的 Sir Andrew Fountaine 提及列为同一人物主项。",
                "original_quotes": [{"source_span": "F.csv#75", "text": "Fountaine, Sir Andrew"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/03-Index/03-2-Index-CSV/F.csv", "source_span": "F.csv#75"},
            },
            {
                "citation": BOOK,
                "location": "第10章 p.279；S2 lines 43–49",
                "sentence_summary": "Haskell称其为富有的收藏家和鉴赏家，曾广泛游历欧洲，并称 Narford Hall 为其乡间居所。",
                "original_quotes": [{"source_span": "S2 lines 43–49; print p.279", "text": "the country seat of the most interesting of all their English patrons, Sir Andrew Fountaine, a rich collector and connoisseur who had travelled widely in Europe"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md", "source_span": "lines 43–49; print p.279"},
            },
            {
                "citation": BOOK,
                "location": "第13章 p.343 注3；S2 line 237",
                "sentence_summary": "注释将 Sir Andrew Fountaine 列入 Zanetti 木刻图版集的受赠者名单，但未将个人与某一具体图版配对。",
                "original_quotes": [{"source_span": "S2 line 237; print p.343 n.3", "text": "Among these were Mariette, Crozat, Vleughels, the Duke of Devonshire, Sir Andrew Fountaine, Dr Richard Mead, Joseph Smith, Rosalba Carriera and Zaccaria Sagredo."}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md", "source_span": "line 237; print p.343 n.3"},
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=1000)
    body = """## 内容

### 描述

**中文：** Haskell第10章称 Sir Andrew Fountaine 为富有的收藏家和鉴赏家，曾广泛游历欧洲，并将 Narford Hall 记为其乡间居所。第13章注3把他列入 Zanetti 木刻图版集受赠者名单；该注没有说明哪一具体图版赠给哪位个人。索引 F.csv#75 将第10章 p.279 与第13章 p.343 注3列于同一人物主项。中文名为本项目工作音译，身份说明限于书内材料。

**English:** Haskell describes Sir Andrew Fountaine in Chapter 10 as a wealthy collector and connoisseur who travelled widely in Europe, and identifies Narford Hall as his country seat. Chapter 13, note 3, includes him among recipients of Zanetti’s woodcut set without assigning a particular sheet to each person. Index F.csv#75 lists Chapter 10, p. 279, and Chapter 13, p. 343 n. 3 under the same person entry. The Chinese name is a working transliteration, and the identification is limited to the book.

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| 原文全名 | Sir Andrew Fountaine | S1（第10章 p.279；索引 F.csv#75） |

### 身份

| 字段 | 值 | 证据 |
|---|---|---|
| 本书称谓 | Rich collector and connoisseur（富有的收藏家、鉴赏家） | S1（第10章 p.279） |
| 乡间居所 | Narford Hall | S1（第10章 p.279） |

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。Narford Hall 与 Fountaine 的乡间居所关系候选 st-chp10-p279-narford-seat-fountaine 留待 S6；第13章受赠者名单陈述 st-chp13-p343-notes-note3-named-dedicatees 不将个人与具体图版配对，暂不据此建立逐件关系。逐组记录见[过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-andrew-fountaine-20261017)。
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
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    af, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    mf, manifest = sync.read_csv(MANIFEST)
    candidate = next(row for row in candidates if row["candidate_id"] == CID)
    matches = [r for r in alignments if r.get("candidate_id") == CID and not r.get("external_source")]
    assert len(matches) == 1
    alignment = matches[0]
    assert candidate["suggested_type"] == "person" and candidate["index_entry_id"] == "F.csv#75"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_members = [r["candidate_id"] for r in alignments if r.get("candidate_id") and not r.get("external_source") and r["decision"] == "new" and sync.get_group(r.get("resolution_note", "")) == GROUP]
    assert group_members == [CID]
    assert not any(r.get("ku_id") == KU for r in manifest) and not (ROOT / CARD).exists()

    statements = [json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    direct = {r["statement_id"] for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and CID in (r.get("subject_candidate_id"), r.get("object_candidate_id"))}
    related = {r["statement_id"] for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and CID in (r.get("qualifiers") or {}).get("mentioned_candidate_ids", [])}
    assert direct == DIRECT and RELATED.issubset(related)

    accepted = ACCEPTED.read_text(encoding="utf-8-sig").splitlines()
    assert f"- {CARD}" not in accepted
    planned = [dict(r) for r in alignments]
    target = next(r for r in planned if r.get("alignment_id") == alignment["alignment_id"])
    target["ku_id"] = KU
    target["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    target["resolution_note"] += f" S4登记（{DATE}）：{GROUP} 映射至 {KU}；F.csv#75 将第10章 p.279 与第13章 p.343 注3列为同一人物条目。本书所载称谓及 Narford Hall 语境入卡；关系候选仍待 S6。"
    planned_manifest = sorted([*manifest, {"ku_id": KU, "type": "person", "canonical_name": "安德鲁·方丹", "name_en": "Sir Andrew Fountaine", "source_task": TASK, "card_path": CARD}], key=lambda row: row["ku_id"])
    planned_accepted = insert_accepted(accepted, CARD)
    card = make_card()
    header = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert header and isinstance(yaml.safe_load(header.group(1)), dict)

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(value[key] for value in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] == 696 and totals["registered_members"] == 857
    assert totals["pending_groups"] == 4088 and totals["pending_members"] == 4110
    assert len(planned_manifest) == len(manifest) + 1
    process_text = process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 person：Sir Andrew Fountaine 跨章身份组登记（{DATE}）\n\n"
        f"cand-1060（F.csv#75，索引页码279、343n）保持单成员 new 组 {GROUP}，登记为[安德鲁·方丹爵士（Sir Andrew Fountaine）](../../../{CARD})（{KU}）。"
        "第10章 p.279给出全名、收藏家／鉴赏家称谓并称 Narford Hall 为其乡间居所；第13章 p.343 注3列其为 Zanetti 木刻图版集的受赠者之一，但未将其对应到某件图版。\n"
        f"- 直接关系候选 {', '.join(sorted(DIRECT))} 留待 S6；受赠者集合陈述 {', '.join(sorted(RELATED - DIRECT))} 不作逐件配对，未新增 formal relations。\n"
        f"- S4 登记后：{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记，{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记。"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text, n = re.subn(r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)", rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>", result_text, count=1)
    assert n == 1
    result_text += (
        f"\n\n### S3/S4 person：Sir Andrew Fountaine 跨章身份组登记（{DATE}）\n\n"
        f"{CID} → [安德鲁·方丹爵士（Sir Andrew Fountaine）](../units/persons/andrew-fountaine.md)；F.csv#75将第10章 p.279与第13章 p.343 注3列为同一人物主项；关系候选留待 S6。"
    )

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
