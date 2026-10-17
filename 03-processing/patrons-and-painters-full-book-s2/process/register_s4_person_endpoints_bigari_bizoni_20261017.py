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
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/B.csv"
GROUPS = {
    "bigari": {
        "candidate": "cand-0374",
        "group": "new-person:bigari-vittorio-2e86eea2d2",
        "ku_id": "units/persons/vittorio-bigari",
        "name_zh": "维托里奥·比加里",
        "name_en": "Vittorio Bigari",
        "card": "04-knowledge/units/persons/vittorio-bigari.md",
        "anchor": "s4-person-vittorio-bigari-endpoint-20261017",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "location": "第8章，印刷页222；OCR L129",
        "quote": "Vittorio Bigari, known primarily for his later architectural fantasies, painted a fresco of the Catholic Religion",
        "summary": "Haskell 将 Vittorio Bigari 称为 Bolognese artist，并称其绘制了寓意天主教的天花壁画。",
        "description_zh": (
            "Haskell 在第8章 p.222 称 Vittorio Bigari 为 Bolognese artist，记载他绘制一幅以教皇统辖 Ravenna、Bologna 与 Ferrara 象征天主教的天花壁画。"
            "原书还称他主要以较晚期的建筑幻想画知名。本卡仅记录书内人物称谓与语境，不确认壁画现状、题名或外部生平。"
        ),
        "description_en": (
            "In Chapter 8, p.222, Haskell identifies Vittorio Bigari as a Bolognese artist and says he painted a ceiling fresco representing the Catholic Religion through the Papacy presiding over Ravenna, Bologna, and Ferrara. "
            "Haskell also says Bigari was known primarily for his later architectural fantasies. This card records the person and context in the book; it does not verify the fresco’s present state, title, or external biography."
        ),
        "index_ref": "B.csv#221",
        "index_quote": "Bigari, Vittorio",
        "relation_ids": {"st-chp8-p222-bigari-paints-catholic-religion-fresco"},
        "process_summary": "第8章 p.222 正文与索引 B.csv#221 均给出 Vittorio Bigari 全名；正文称其为 Bolognese artist 并记载天花壁画。人物身份清楚，作品归属关系仍按 S2 候选待审。",
    },
    "bizoni": {
        "candidate": "cand-0377",
        "group": "new-person:bernardo-bizoni-e54061a723",
        "ku_id": "units/persons/bernardo-bizoni",
        "name_zh": "贝尔纳多·比佐尼",
        "name_en": "Bernardo Bizoni",
        "card": "04-knowledge/units/persons/bernardo-bizoni.md",
        "anchor": "s4-person-bernardo-bizoni-endpoint-20261017",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_i.md",
        "location": "第2章，印刷页30，注1；OCR L147",
        "quote": "See the remarkable journal kept by Giustiniani’s friend Bernardo Bizoni published by Anna Banti.",
        "summary": "Haskell 的脚注称 Giustiniani 的朋友 Bernardo Bizoni 撰写的一份 journal 由 Anna Banti 出版；未给出书名或版本。",
        "description_zh": (
            "Haskell 第2章 p.30 注1称 Bernardo Bizoni 是 Giustiniani 的朋友，并提到一份由 Anna Banti 出版、由 Bizoni 记述的 journal。"
            "书后索引 B.csv#224 将其定位至该注释。本卡只记录来源所给姓名和称谓，不补出 journal 的题名、版本或 Bizoni 的外部生平。"
        ),
        "description_en": (
            "Chapter 2, p.30 note 1, calls Bernardo Bizoni a friend of Giustiniani and refers to a journal kept by Bizoni and published by Anna Banti. "
            "The index entry B.csv#224 points to the note. This card records the name and description in Haskell’s source without supplying a title or edition for the journal or an external biography of Bizoni."
        ),
        "index_ref": "B.csv#224",
        "index_quote": "Bizoni, Bernardo",
        "relation_ids": {
            "st-chp2-seci-l124-157-bizoni-kept-journal",
            "st-chp2-seci-l124-157-giustiniani-friend-bizoni",
        },
        "process_summary": "第2章 p.30 注1与索引 B.csv#224 均以全名指向 Bernardo Bizoni；注释称其为 Giustiniani 的朋友和 journal keeper，但未给出出版物题名。人物身份可登记，友谊及 journal 相关候选关系留待 S6。",
    },
}


def insert_accepted(lines: list[str], card_rel: str) -> list[str]:
    entry = f"- {card_rel}"
    assert entry not in lines
    units_idx = lines.index("units:")
    claims_idx = next(
        (i for i in range(units_idx + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])),
        len(lines),
    )
    insert_at = next(
        (i for i in range(units_idx + 1, claims_idx) if lines[i].startswith("- ") and lines[i][2:] > card_rel),
        claims_idx,
    )
    lines.insert(insert_at, entry)
    return lines


def make_card(spec: dict) -> str:
    source_ref = "../../../" + spec["source_file"]
    index_ref = f"../../../{INDEX_FILE}"
    process_ref = f"03-processing/{TASK}/process/knowledge.md#{spec['anchor']}"
    fm = yaml.safe_dump({
        "title": f"{spec['name_zh']}（{spec['name_en']}）",
        "name_en": spec["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": spec["location"],
                "sentence_summary": spec["summary"],
                "original_quotes": [{"source_span": spec["location"], "text": spec["quote"]}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": spec["source_file"],
                    "source_span": spec["location"],
                },
            },
            {
                "citation": "Francis Haskell, *Patrons and Painters*, index.",
                "location": f"全书索引 {spec['index_ref']}",
                "sentence_summary": f"索引以 {spec['index_quote']} 定位相关正文或注释。",
                "original_quotes": [{"source_span": spec["index_ref"], "text": spec["index_quote"]}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": INDEX_FILE,
                    "source_span": spec["index_ref"],
                },
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": process_ref,
    }, allow_unicode=True, sort_keys=False, width=1000)
    relations = ", ".join(sorted(spec["relation_ids"]))
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {spec['description_zh']}〔[来源正文]({source_ref})；[索引 {spec['index_ref']}]({index_ref})〕

**English:** {spec['description_en']} ([source text]({source_ref}); [index {spec['index_ref']}]({index_ref}))

### 身份与来源边界

- 候选 {spec['candidate']} 保持单成员 S3 new 组 {spec['group']}；身份由正文全名与索引定位支持。
- 本卡不把书内描述扩大为外部履历，也不补充来源未提供的出版物或作品细节。

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。直接 S2 关系候选（{relations}）留待 S6；KU 登记不代表关系裁决。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{spec['anchor']})。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register two person relation endpoints with their one-member S3 groups.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    planned_alignments = [dict(row) for row in alignments]
    cards = {}
    planned_manifest = list(manifest)
    planned_accepted = list(accepted_lines)

    for spec in GROUPS.values():
        cid = spec["candidate"]
        candidate = candidate_by_id[cid]
        decision = next(row for row in planned_alignments if row.get("candidate_id") == cid and not row.get("external_source"))
        assert candidate["suggested_type"] == "person"
        assert decision["decision"] == "new" and not decision.get("ku_id")
        assert sync.get_group(decision.get("resolution_note", "")) == spec["group"]
        group_members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == spec["group"]
        ]
        assert group_members == [cid]
        assert candidate["canonical_name"] in ("Bigari, Vittorio", "Bizoni, Bernardo")
        assert not any(row.get("ku_id") == spec["ku_id"] for row in manifest)
        assert not any(row.get("type") == "person" and row.get("name_en", "").casefold() == spec["name_en"].casefold() for row in manifest)
        assert not (ROOT / spec["card"]).exists()
        assert spec["card"] not in planned_accepted

        body = (ROOT / spec["source_file"]).read_text(encoding="utf-8-sig")
        index = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
        if cid == "cand-0374":
            assert candidate["index_entry_id"] == "B.csv#221"
            assert "Vittorio Bigari, known primarily for his later architectural fantasies" in body
            assert '"Bigari, Vittorio"' in index
        else:
            assert candidate["index_entry_id"] == "B.csv#224"
            assert "Giustiniani’s friend Bernardo Bizoni" in body
            assert '"Bizoni, Bernardo"' in index

        direct = {
            row["statement_id"] for row in statements
            if (row.get("qualifiers") or {}).get("relation_candidate") is True
            and cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
        }
        assert direct == spec["relation_ids"]
        decision["ku_id"] = spec["ku_id"]
        decision["process_ref"] = f"{TASK}#{spec['anchor']}"
        decision["resolution_note"] += (
            f" S4登记（{DATE}）：{spec['group']} 映射至 {spec['ku_id']}；已创建来源限定 person KU。"
            f"{len(direct)} 条直接关系候选保留待 S6。"
        )
        cards[spec["card"]] = make_card(spec)
        planned_manifest.append({
            "ku_id": spec["ku_id"],
            "type": "person",
            "canonical_name": spec["name_zh"],
            "name_en": spec["name_en"],
            "source_task": TASK,
            "card_path": spec["card"],
        })
        planned_accepted = insert_accepted(planned_accepted, spec["card"])
        fm_match = re.match(r"\A---\n(.*?)\n---\n", cards[spec["card"]], re.DOTALL)
        assert fm_match and isinstance(yaml.safe_load(fm_match.group(1)), dict)

    planned_manifest.sort(key=lambda row: row["ku_id"])
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["same_candidates"] == 1891
    assert totals["new_candidates"] == 4968
    assert totals["new_groups"] == 4785
    assert totals["registered_groups"] == 674
    assert totals["registered_members"] == 835
    assert totals["pending_groups"] == 4111
    assert totals["pending_members"] == 4133

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    additions = []
    for spec in GROUPS.values():
        assert f'<a id="{spec["anchor"]}"></a>' not in process_text
        additions.append(
            f"<a id=\"{spec['anchor']}\"></a>\n\n### S3/S4 person：{spec['name_en']} 直接关系端点登记（{DATE}）\n\n"
            f"{spec['candidate']} 保持单成员 new 组 {spec['group']}，登记为 [{spec['name_zh']}（{spec['name_en']}）]"
            f"(../../../{spec['card']})（{spec['ku_id']}）。{spec['process_summary']}\n"
            f"- 直接关系候选（{', '.join(sorted(spec['relation_ids']))}）留待 S6；未写入 formal relations。"
        )
    process_text = process_text.rstrip() + "\n\n" + "\n\n".join(additions) + (
        f"\n\nS4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
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
    result_text += "\n\n### S3/S4 person：Bigari 与 Bizoni 直接关系端点登记（2026-10-17）\n\n"
    result_text += "；".join(
        f"{spec['candidate']} → [{spec['name_zh']}（{spec['name_en']}）](../units/persons/{Path(spec['card']).stem}.md)"
        for spec in GROUPS.values()
    ) + "。双语卡只记录书内姓名和语境；各自的直接关系候选留待 S6。"

    assert len(planned_manifest) == len(manifest) + len(GROUPS)
    if args.dry_run:
        print(
            f"dry-run passed: groups={len(GROUPS)}; direct_relation_candidates=3; manifest={len(manifest)}->{len(planned_manifest)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}"
        )
        return 0

    for card_rel, card in cards.items():
        (ROOT / card_rel).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups={len(GROUPS)}; manifest={len(planned_manifest)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
