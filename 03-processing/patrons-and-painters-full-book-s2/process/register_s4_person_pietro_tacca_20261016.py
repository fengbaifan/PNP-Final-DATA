from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import shutil
import sys
from io import StringIO
from pathlib import Path

import yaml

PROCESS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

GROUP = "new-person:pietro-tacca-374a1e8a84"
CANDIDATES = ("cand-2537", "cand-2538")
ALIGNMENT_IDS = ("aln-2872", "aln-2873")
KU_ID = "units/persons/pietro-tacca"
CARD_REL = "04-knowledge/units/persons/pietro-tacca.md"
CARD_PATH = ROOT / CARD_REL
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-pietro-tacca-20261016"

BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv_text(fieldnames, rows) -> str:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    if any(line.strip() == f"- {CARD_REL}" for line in lines):
        raise ValueError("Accepted path already exists.")
    insert_at = next(
        (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "全书索引 T.csv#0–1；#0列pp.97、174、178，#1列pp.387、389",
            "sentence_summary": "索引主项为Tacca, Pietro；子项指向涉及Paolo Giordano Orsini委托的文献，并列相关正文页码。",
            "original_quotes": [
                {"source_span": "T.csv#0", "text": "Tacca, Pietro"},
                {
                    "source_span": "T.csv#1",
                    "text": "documents relating to commissions from Paolo Giordano Orsini, Duke of Bracciano",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/T.csv",
                "source_span": "T.csv#0–1",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第4章 p.97；正文L29、附注6 L57",
            "sentence_summary": "Haskell称Paolo Giordano希望向Tacca取得骑马像，并说Tacca送来modello；注6称附录刊出一封Tacca致Paolo Giordano的信。文本未说明该拟议骑马像是否完成。",
            "original_quotes": [
                {"source_span": "line 29; print p. 97", "text": "who sent him a modello."},
                {
                    "source_span": "line 57; print p. 97, note 6",
                    "text": "I can find no reference to this work in Tacca literature, and in Appendix 2 I publish the letter from him to Paolo Giordano.",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/04_CHP-4_sec_i.md",
                "source_span": "lines 29, 57; print p. 97",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第7章 pp.174、178；正文L54、105",
            "sentence_summary": "Haskell称Tacca与Francavilla共同完成Henri IV骑马纪念碑，并称Tacca为雕塑家；另述Charles I曾希望请他赴伦敦制作两匹马，但托斯卡纳大公拒绝准其出行。后者不证明正式委托或作品完成。",
            "original_quotes": [
                {
                    "source_span": "line 54; print p. 174",
                    "text": "the monument, which was completed by Pietro Tacca and Francavilla",
                },
                {
                    "source_span": "line 105; print p. 178",
                    "text": "the sculptor Pietro Tacca whom he wished to come to London ‘to make two horses for him’; the Grand Duke of Tuscany refused to authorise the visit.",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "source_span": "lines 54, 105; print pp. 174, 178",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第19章附录2 p.389；OCR L70–75，档案标识按Haskell刊本",
            "sentence_summary": "Haskell刊出一封署名Pietro Tacca、署于1624年12月30日佛罗伦萨的信，涉及马模型装箱寄送和若改作铜像时的条件方案；所引档案原件未独立查阅。",
            "original_quotes": [
                {
                    "source_span": "line 72; print p. 389, item 172 c.306",
                    "text": "Se bene era assai dificile poter mandare il modello del Cavallo senza pericolo di guastarsi",
                },
                {"source_span": "lines 73–75; print p. 389", "text": "di firenze li 30 di Xbre 1624.\nDi V.E. Ill.ma Humiliss.mo Serv.re\nPietro Tacca"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md",
                "source_span": "lines 70–75; print p. 389",
            },
        },
    ]
    frontmatter = {
        "title": "皮埃特罗·塔卡（Pietro Tacca）",
        "name_en": "Pietro Tacca",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    idx = "[全书索引 T.csv#0–1](../../../02-sources/03-Index/03-2-Index-CSV/T.csv)"
    ch4 = "[第4章 p.97](../../../02-sources/02-Markdown/04_CHP-4_sec_i.md)（L29、57）"
    ch7 = "[第7章 pp.174、178](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L54、105）"
    ch19 = "[第19章附录2 p.389](../../../02-sources/02-Markdown/19_CHP-19Appendix.md)（L70–75）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录全书索引中的 Pietro Tacca（索引形式 Tacca, Pietro）；第7章称其为雕塑家。其姓名见于第4、7章正文及第19章附录所录书信。中文展示名为项目工作音译。{idx} {ch4} {ch7} {ch19}

**English:** This unit records Pietro Tacca, indexed as “Tacca, Pietro”; Chapter 7 identifies him as a sculptor. His name appears in Chapters 4 and 7 and in a letter reproduced in the Chapter 19 appendix. The Chinese display name is a project working transliteration. {idx} {ch4} {ch7} {ch19}

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Pietro Tacca | S1，T.csv#0 |
| 索引形式 | Tacca, Pietro | S1，T.csv#0 |
| 身份 | 雕塑家 | S2，第7章 p.178 |

### 本书相关语境

第4章叙述骑马像模型及一封致Paolo Giordano的信；第7章记载纪念碑、雕塑工作与未获准的赴英计划；第19章附录刊载一封Tacca署名的1624年信件。附录文字依据Haskell刊本，未独立查阅所引档案原件；方案性陈述不表示相应作品已经完成。相关人物、作品及委托陈述仍以原书statement为依据，逐条关系待审。{ch4} {ch7} {ch19}

The book discusses a modello and a letter addressed to Paolo Giordano in Chapter 4; a monument, sculptural work, and an unapproved plan to travel to England in Chapter 7; and a letter signed by Tacca in the Chapter 19 appendix. The appendix text is reproduced by Haskell; the cited archival manuscript has not been independently consulted. Proposed work is not treated as completed. Statements about people, works, and commissions remain tied to their book evidence and await item-by-item relation review. {ch4} {ch7} {ch19}

## 关系与证据

### 身份与外部链接

本卡仅登记书内身份依据；当前没有外部身份链接。

This unit records identity evidence from the book; no external identity link is currently recorded.

### 关系记录

当前没有正式关系记录。书内直接关系候选保留在断言账本中，尚未转为正式关系。

No formal relations are recorded. Direct relation candidates from the book remain in the statement ledger and have not been converted into formal relations.
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Pietro Tacca identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment = read_csv(ALIGNMENT)
    manifest_fields, manifest = read_csv(MANIFEST)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    assert all(candidate_by_id[cid].get("suggested_type") == "person" for cid in CANDIDATES)
    group_rows = [
        row for row in alignment
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and f"group={GROUP}" in row.get("resolution_note", "")
    ]
    assert sorted(row["candidate_id"] for row in group_rows) == sorted(CANDIDATES)
    assert sorted(row["alignment_id"] for row in group_rows) == sorted(ALIGNMENT_IDS)
    assert all(not row.get("ku_id") for row in group_rows)
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not any(
        row.get("type") == "person" and row.get("name_en", "").casefold() == "pietro tacca"
        for row in manifest
    )
    assert not CARD_PATH.exists()
    assert not any(line.strip() == f"- {CARD_REL}" for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines())

    index_text = (ROOT / "02-sources/03-Index/03-2-Index-CSV/T.csv").read_text(encoding="utf-8-sig")
    ch4 = (ROOT / "02-sources/02-Markdown/04_CHP-4_sec_i.md").read_text(encoding="utf-8-sig")
    ch7 = (ROOT / "02-sources/02-Markdown/07_CHP-7_sec_i.md").read_text(encoding="utf-8-sig")
    ch19 = (ROOT / "02-sources/02-Markdown/19_CHP-19Appendix.md").read_text(encoding="utf-8-sig")
    assert "Tacca, Pietro" in index_text and "documents relating to commissions from Paolo Giordano Orsini" in index_text
    assert "who sent him a modello" in ch4 and "publish the letter from him to Paolo Giordano" in ch4
    assert "completed by Pietro Tacca and Francavilla" in ch7 and "the sculptor Pietro Tacca" in ch7
    assert "Pietro Tacca" in ch19 and "di firenze li 30 di Xbre" in ch19

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct_statements = [
        row for row in statements
        if row.get("subject_candidate_id") in CANDIDATES or row.get("object_candidate_id") in CANDIDATES
    ]
    relation_candidates = [
        row for row in direct_statements
        if row.get("qualifiers", {}).get("relation_candidate")
    ]
    assert len(direct_statements) == 7 and len(relation_candidates) == 7

    planned_alignment = [dict(row) for row in alignment]
    for mapped in planned_alignment:
        if mapped.get("alignment_id") in ALIGNMENT_IDS:
            assert mapped.get("candidate_id") in CANDIDATES and mapped.get("decision") == "new"
            mapped["ku_id"] = KU_ID
            mapped["resolution_note"] += f" S4 registration ({DATE}): mapped this new-person group to {KU_ID}."
    planned_manifest = [dict(row) for row in manifest] + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "皮埃特罗·塔卡",
        "name_en": "Pietro Tacca",
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    planned_manifest.sort(key=lambda row: row["ku_id"])
    accepted_text = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))
    card_text = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card_text, re.DOTALL)
    assert frontmatter_match
    card_frontmatter = yaml.safe_load(frontmatter_match.group(1))
    assert card_frontmatter["type"] == "person" and len(card_frontmatter["sources"]) == 4

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_insert = (
        f"### S4 person：Pietro Tacca 跨章双候选组登记（{DATE}）\n\n"
        f"- `cand-2537`（T.csv#0，pp.97、174、178）与 `cand-2538`（T.csv#1，pp.387、389）保持S3组 `{GROUP}`，共同映射至 `{KU_ID}`。既有manifest无同名person；两候选全名、章节正文称名及附录署名相合。新卡不补外部身份或书外生平。\n"
        f"- 第4、7、19章的模型、纪念碑、雕塑活动和书信内容保留原S2 statements；附录信仅按Haskell刊本记录，档案原件未独立查阅。7条直接关系候选均留待S6，本轮未新增正式关系。\n"
        f"- `build_field_facts.py` 预检无警告并apply新增3条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。\n\n"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, result_insert + marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：Pietro Tacca 跨章双候选组登记（{DATE}）"
    assert process_heading not in process_text
    process_text += (
        f"\n\n{process_heading}\n\n"
        f"- `cand-2537`（T.csv#0）与 `cand-2538`（T.csv#1）保持S3组 `{GROUP}`，共同登记为 `{KU_ID}`。索引主项、跨第4、7章的正文全名及第19章附录签名相互支持同一人物身份；现有manifest和person卡均无同名对象。\n"
        "- 卡片限于索引全名、索引形式和书内雕塑家身份。第4章p.97报告模型发送和附注所述通信；第7章pp.174、178记载纪念碑、雕塑身份及赴英计划被拒；第19章p.389刊出Tacca署名的1624年信件。该信的原档案未独立查阅，方案不视为完成作品。\n"
        "- 7条直接S2陈述均标为关系候选，全部留待S6逐条审查。本轮不写入 `relations.csv`，不推定未完成雕塑、作品存世或手稿已核。\n"
        f"- `build_field_facts.py` 预检无警告并apply新增3条source-backed字段记录，来源数不变、unverified保持1,578。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；manifest={len(planned_manifest)}。\n"
    )

    outputs = {
        ALIGNMENT: write_csv_text(alignment_fields, planned_alignment),
        MANIFEST: write_csv_text(manifest_fields, planned_manifest),
        ACCEPTED: accepted_text,
        CARD_PATH: card_text,
        PROCESS: process_text,
        RESULT: result_text,
    }
    for path in outputs:
        assert not path.with_name(path.name + BACKUP_SUFFIX).exists()

    if args.dry_run:
        for path, updated in outputs.items():
            current = path.read_text(encoding="utf-8-sig") if path.exists() else ""
            diff = difflib.unified_diff(
                current.splitlines(keepends=True), updated.splitlines(keepends=True),
                fromfile=str(path.relative_to(ROOT)), tofile=str(path.relative_to(ROOT)) + " (updated)", n=2,
            )
            print("".join(diff), end="")
        print(
            f"dry-run passed: {','.join(CANDIDATES)}->{GROUP}->{KU_ID}; registered="
            f"{totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
            f"direct_statements={len(direct_statements)}; relation_candidates={len(relation_candidates)}"
        )
        return 0

    backups = []
    try:
        for path in outputs:
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if path.exists():
                shutil.copy2(path, backup)
            else:
                backup.write_text("NEW FILE: created by S4 Pietro Tacca registration\n", encoding="utf-8")
            backups.append((path, backup))
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8", newline="\n")
    except Exception:
        for path, backup in backups:
            if backup.read_text(encoding="utf-8-sig").startswith("NEW FILE:"):
                if path.exists():
                    path.unlink()
            else:
                shutil.copy2(backup, path)
        raise

    print(
        f"applied: {','.join(CANDIDATES)}->{GROUP}->{KU_ID}; registered={totals['registered_groups']}/"
        f"{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}; direct_statements={len(direct_statements)}; "
        f"relation_candidates={len(relation_candidates)}; backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
