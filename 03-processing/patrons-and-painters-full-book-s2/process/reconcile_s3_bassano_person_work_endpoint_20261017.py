from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
BACKLOG_PATH = TABLES / "candidate-backlog.csv"
CANDIDATES_PATH = TABLES / "entity-candidates.csv"
MENTIONS_PATH = TABLES / "mentions.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

PERSON_GROUP = "new-person:bassano-jacopo-0104694cf4"
PERSON_KU = "units/persons/jacopo-bassano"
PERSON_CARD = "04-knowledge/units/persons/jacopo-bassano.md"
WORK_CANDIDATE = "cand-12428"
WORK_ALIGNMENT = "aln-12632"
WORK_GROUP = "new-work:bassano-nativity-s-giorgio-maggiore-20261017"
WORK_KU = "units/works/jacopo-bassano-nativity-s-giorgio-maggiore"
WORK_CARD = "04-knowledge/units/works/jacopo-bassano-nativity-s-giorgio-maggiore.md"
WORK_STATEMENT = "st-chp10-p313-guardi-copied-bassano-nativity"
WORK_MENTION = "m-s2-ch10-p313-0020"
PERSON_MENTION = "m-s2-ch10-p313-0019"


def make_card(title: str, name_en: str, kind: str, sources: list[dict], body: str) -> str:
    frontmatter = {
        "title": f"{title}（{name_en}）",
        "name_en": name_en,
        "type": kind,
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK,
                "location": item["location"],
                "sentence_summary": item["summary"],
                "original_quotes": [
                    {"source_span": span, "text": quote}
                    for span, quote in item.get("quotes", [])
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": item["source_file"],
                    "source_span": item["span"],
                },
            }
            for item in sources
        ],
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    return f"---\n{yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)}---\n\n## 内容\n\n{body}"


PERSON_SOURCES = [
    {
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_iii.md",
        "location": "第5章；印刷页134；OCR L24–25",
        "span": "lines 24–25; print p. 134",
        "summary": "Haskell 将 Bassano 与 Caravaggio 并列为可能的先例；原文明确保留 perhaps 的限定。",
        "quotes": [("lines 24–25", "Bassano and Caravaggio perhaps")],
    },
    {
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "location": "第10章；印刷页313；OCR L73–75",
        "span": "lines 73–75; print p. 313",
        "summary": "Haskell 在 Guardi 被要求临摹的威尼斯大师作品清单中称 ‘Bassano’s Nativity in S. Giorgio Maggiore’；人物与画作分别登记。",
        "quotes": [("lines 73–75", "Veronese’s Marriage at Cana in S. Giorgio Maggiore and Madonna and Child with Saints in S. Zaccaria, Tintoretto’s Temperance and Fortitude in the Madonna dell’Orto, Bassano’s Nativity in S. Giorgio Maggiore")],
    },
    {
        "source_file": "02-sources/02-Markdown/22_CHP-22Index.md",
        "location": "书后索引；条目 B.csv#104–105",
        "span": "index entries Bassano, Jacopo; Bassano, Jacopo / Nativity",
        "summary": "B.csv#104 以 Jacopo Bassano 汇集第134、222、231、262、340、376页；B.csv#105 是同名人物的 Nativity 子项，定位第313页。",
        "quotes": [
            ("index entry B.csv#104", "Bassano, Jacopo, 134, 222, 231, 262, 340, 376"),
            ("index entry B.csv#105", "Nativity, 313"),
        ],
    },
]

WORK_SOURCES = [
    {
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "location": "第10章；印刷页313；OCR L73–75",
        "span": "lines 73–75; print p. 313",
        "summary": "Haskell 将 Bassano’s Nativity in S. Giorgio Maggiore 列为 Francesco Guardi 被要求临摹的威尼斯大师作品之一；没有指明 Guardi 临摹的具体版本或日期。",
        "quotes": [("lines 73–75", "In general, he was required to copy masterpieces of the Venetian Cinquecento—Veronese’s Marriage at Cana in S. Giorgio Maggiore and Madonna and Child with Saints in S. Zaccaria, Tintoretto’s Temperance and Fortitude in the Madonna dell’Orto, Bassano’s Nativity in S. Giorgio Maggiore—and even pictures by his own contemporaries, Sebastiano Ricci, Piazzetta and Rosalba Camera.")],
    },
]

PERSON_BODY = """### 描述

**中文：** 本卡对应书后索引 B.csv#104、#105 的 Jacopo Bassano 人物条目。第5章 p.134 只以姓氏称其为一项可能的艺术先例；第10章 p.313 又以所有格称 “Bassano’s Nativity”。后一个短语同时指向人物与一件作品：人物由索引条目定位，作品另登记为[《Bassano’s Nativity》（S. Giorgio Maggiore）](../works/jacopo-bassano-nativity-s-giorgio-maggiore.md)。此卡不把绘画作品当作人物身份，也不补充外部生平。[第5章 p.134](../../../02-sources/02-Markdown/05_CHP-5_sec_iii.md)（L24–25）；[第10章 p.313](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L73–75）；[书后索引](../../../02-sources/02-Markdown/22_CHP-22Index.md)（L355–356）

**English:** This card represents the Jacopo Bassano person entries B.csv#104 and #105 in the index. Chapter 5, p.134, refers to Bassano by surname as a possible artistic precedent; Chapter 10, p.313, uses the possessive “Bassano’s Nativity.” That phrase refers both to the painter and to a work: the person is resolved through the index, and the painting is registered separately as [*Bassano’s Nativity* at S. Giorgio Maggiore](../works/jacopo-bassano-nativity-s-giorgio-maggiore.md). This card does not treat the painting as the person or add external biography. [Chapter 5, p.134](../../../02-sources/02-Markdown/05_CHP-5_sec_iii.md) (L24–25); [Chapter 10, p.313](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md) (L73–75); [Index](../../../02-sources/02-Markdown/22_CHP-22Index.md) (L355–356)

### 名称与身份边界

- 对应人物候选 `cand-0257`（B.csv#104）与 `cand-0258`（B.csv#105）；两条索引记录均给出同一全名 Jacopo Bassano，#105 的 “Nativity” 是作品子项，不是另一位人物。
- `m-s2-ch10-p313-0019` 的 “Bassano” 映射到人物；`m-s2-ch10-p313-0020` 的 “Nativity” 已改映射到独立 work 候选 `cand-12428`。
- 不据索引外扩绘画生卒、创作日期或其他版本身份。

### 关系与证据

`st-chp5-p134-bassano-caravaggio-precedents` 是人物卡唯一直接 S2 关系候选。Haskell 的先例判断保留 “perhaps” 限定，留待 S6；第10章的 Guardi 临摹陈述现以作品为 object，不再误连到人物。本卡未新增正式关系。
"""

WORK_BODY = """### 描述

**中文：** 本卡登记 Haskell 第10章 p.313 所称 “Bassano’s Nativity in S. Giorgio Maggiore”。作者把它列为 Francesco Guardi 被要求临摹的威尼斯大师作品之一。卡名是据画家、题材和地点生成的描述性名称；原书没有给出更完整的作品题名、创作日期、现存版本或 Guardi 临摹件信息。[第10章 p.313](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L73–75）

**English:** This card represents the work Haskell calls “Bassano’s Nativity in S. Giorgio Maggiore” on p.313 of Chapter 10. The author lists it among Venetian Cinquecento masterpieces that Francesco Guardi was required to copy. The card uses a descriptive title based on the painter, subject, and source-stated location; the book does not provide a fuller title, creation date, surviving version, or details about Guardi’s copy. [Chapter 10, p.313](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md) (L73–75)

### 作品身份与范围

- 对应新候选 `cand-12428`，由 backlog `bl-0004` 按 S1→S3→S4 完成；S3 组 `new-work:bassano-nativity-s-giorgio-maggiore-20261017`。
- 作品位置按原文保留为 S. Giorgio Maggiore；不据此推断该画目前仍在此地，也不补写题材人物或作者外部身份。
- 与 Jacopo Bassano 人物 KU 分开；也不把 Guardi 的临摹件当作同一作品或新版本。

### 关系与证据

`st-chp10-p313-guardi-copied-bassano-nativity` 是 Francesco Guardi 与此作品之间的直接关系候选，留待 S6 核查方向、委派角色及 “required to copy” 的语义。本轮未新增正式关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Separate Jacopo Bassano from the Nativity work endpoint and register both S4 KUs.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(CANDIDATES_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    backlog_fields, backlog = sync.read_csv(BACKLOG_PATH)
    mention_fields, mentions = sync.read_csv(MENTIONS_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert "cand-0257" in candidate_by_id and "cand-0258" in candidate_by_id
    assert candidate_by_id["cand-0257"]["canonical_name"] == candidate_by_id["cand-0258"]["canonical_name"] == "Bassano, Jacopo"
    assert candidate_by_id["cand-0257"]["suggested_type"] == candidate_by_id["cand-0258"]["suggested_type"] == "person"
    assert all(alignment_by_id[cid]["decision"] == "new" and not alignment_by_id[cid].get("ku_id") for cid in ("cand-0257", "cand-0258"))
    assert all(sync.get_group(alignment_by_id[cid].get("resolution_note", "")) == PERSON_GROUP for cid in ("cand-0257", "cand-0258"))
    assert not any(row.get("ku_id") in {PERSON_KU, WORK_KU} for row in manifest)
    assert not (ROOT / PERSON_CARD).exists() and not (ROOT / WORK_CARD).exists()

    source_text = {
        rel: " ".join((ROOT / rel).read_text(encoding="utf-8-sig").split())
        for rel in {
            "02-sources/02-Markdown/05_CHP-5_sec_iii.md",
            "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
            "02-sources/02-Markdown/22_CHP-22Index.md",
        }
    }
    for item in PERSON_SOURCES + WORK_SOURCES:
        for _, quote in item.get("quotes", []):
            assert " ".join(quote.split()) in source_text[item["source_file"]], (item["location"], quote)
    assert "Bassano, Jacopo, 134, 222, 231, 262, 340, 376" in source_text["02-sources/02-Markdown/22_CHP-22Index.md"]
    assert "Nativity, 313" in source_text["02-sources/02-Markdown/22_CHP-22Index.md"]

    statement_lines = STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
    statement_row = None
    for line in statement_lines:
        data = json.loads(line)
        if data.get("statement_id") == WORK_STATEMENT:
            statement_row = data
            break
    assert statement_row is not None
    assert statement_row["object_candidate_id"] == "cand-0258"
    assert statement_row["qualifiers"]["mentioned_candidate_ids"] == ["cand-1245", "cand-0258", "cand-0732"]

    work_mention = next(row for row in mentions if row.get("mention_id") == WORK_MENTION)
    person_mention = next(row for row in mentions if row.get("mention_id") == PERSON_MENTION)
    assert work_mention["candidate_id"] == "cand-0258" and work_mention["surface_form"] == "Nativity"
    assert person_mention["candidate_id"] == "cand-0257" and person_mention["surface_form"] == "Bassano"

    max_candidate = max(int(row["candidate_id"].split("-")[1]) for row in candidates)
    max_alignment = max(int(row["alignment_id"].split("-")[1]) for row in alignments)
    assert max_candidate == 12427 and max_alignment == 12631
    assert WORK_CANDIDATE not in candidate_by_id and WORK_CANDIDATE == f"cand-{max_candidate + 1:04d}"
    assert WORK_ALIGNMENT == f"aln-{max_alignment + 1:04d}"
    assert not any(row.get("backlog_id") == "bl-0004" for row in backlog)

    planned_candidates = list(candidates)
    new_candidate = {
        "candidate_id": WORK_CANDIDATE,
        "index_entry_id": "",
        "canonical_name": "Jacopo Bassano’s Nativity at S. Giorgio Maggiore",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell lists Bassano’s Nativity in S. Giorgio Maggiore among the Venetian masterpieces Francesco Guardi was required to copy. The card records this source-local painting reference; it does not identify Guardi’s copy, a date, or a surviving version.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-10:10_CHP-10_sec_ii:l72-81#L74",
    }
    planned_candidates.append(new_candidate)

    old_0258_note = alignment_by_id["cand-0258"]["resolution_note"]
    planned_alignments = [dict(row) for row in alignments]
    planned_alignment_by_id = {
        row["candidate_id"]: row for row in planned_alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_alignment_by_id["cand-0258"]["resolution_note"] = (
        "source_ref=candidate=cand-0258;index_entry=B.csv#105;index_pages=313; "
        f"group={PERSON_GROUP}; S3 source-boundary correction 2026-10-17: B.csv#105 names the same person Jacopo Bassano as B.csv#104; "
        f"its ‘Nativity’ subentry is a work locator, not a second person. Body mention {WORK_MENTION} (‘Nativity’) and the copied-work statement endpoint were reassigned to {WORK_CANDIDATE}. "
        f"The person reference ‘Bassano’ remains {PERSON_MENTION} / cand-0257. prior_decision=new; prior_group={PERSON_GROUP}; prior_resolution_note={old_0258_note}"
    )
    planned_alignment_by_id["cand-0257"]["resolution_note"] += (
        " S3 cross-index reconciliation 2026-10-17: grouped with cand-0258, whose B.csv#105 subentry ‘Nativity’ refers to the work; "
        "the person identity remains Jacopo Bassano and the p.313 Nativity artwork is separately represented by cand-12428."
    )
    for cid in ("cand-0257", "cand-0258"):
        planned_alignment_by_id[cid]["ku_id"] = PERSON_KU
        planned_alignment_by_id[cid]["resolution_note"] += f" S4 registration: mapped {PERSON_GROUP} to {PERSON_KU}."
    planned_alignments.append({
        "alignment_id": WORK_ALIGNMENT,
        "candidate_id": WORK_CANDIDATE,
        "ku_id": WORK_KU,
        "external_source": "",
        "external_id": "",
        "decision": "new",
        "accessed_date": "",
        "process_ref": "S3-S4-full-book-2026-10-17",
        "legacy_ku_id": "",
        "resolution_note": (
            f"source_ref=candidate={WORK_CANDIDATE};candidate_source_ref=chp-10:10_CHP-10_sec_ii:l72-81#L74; "
            f"statement={WORK_STATEMENT};group={WORK_GROUP}; New source-local work identity: Haskell names Bassano’s Nativity in S. Giorgio Maggiore as an original Francesco Guardi was required to copy. "
            "No existing same-type work KU matched. The source does not identify Guardi’s copy, its date, or a surviving version. "
            f"S4 registration: mapped {WORK_GROUP} to {WORK_KU}."
        ),
    })

    planned_mentions = [dict(row) for row in mentions]
    next(row for row in planned_mentions if row.get("mention_id") == WORK_MENTION)["candidate_id"] = WORK_CANDIDATE

    planned_statement_lines = list(statement_lines)
    for i, line in enumerate(planned_statement_lines):
        data = json.loads(line)
        if data.get("statement_id") == WORK_STATEMENT:
            data["object_candidate_id"] = WORK_CANDIDATE
            data["qualifiers"]["mentioned_candidate_ids"] = ["cand-1245", "cand-0257", WORK_CANDIDATE, "cand-0732"]
            planned_statement_lines[i] = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            break

    planned_manifest = list(manifest)
    planned_manifest.extend([
        {"ku_id": PERSON_KU, "type": "person", "canonical_name": "雅各布·巴萨诺", "name_en": "Jacopo Bassano", "source_task": TASK, "card_path": PERSON_CARD},
        {"ku_id": WORK_KU, "type": "work", "canonical_name": "巴萨诺《圣诞图》（S. Giorgio Maggiore）", "name_en": "Bassano’s Nativity at S. Giorgio Maggiore", "source_task": TASK, "card_path": WORK_CARD},
    ])

    planned_backlog = list(backlog)
    planned_backlog.append({
        "backlog_id": "bl-0004",
        "canonical_name": "Jacopo Bassano’s Nativity at S. Giorgio Maggiore",
        "suggested_type": "work",
        "status": "completed",
        "source_id": "haskell-1980-rev-ed",
        "source_ref": "chp-10:10_CHP-10_sec_ii:l72-81#L74",
        "statement_id": WORK_STATEMENT,
        "endpoint_role": "painting Francesco Guardi was required to copy",
        "candidate_id": WORK_CANDIDATE,
        "ku_id": WORK_KU,
        "decision_note": "S1/S3/S4 completed in the 2026-10-17 endpoint batch. The source describes a Bassano Nativity at S. Giorgio Maggiore and says Guardi was required to copy it. The S2 object endpoint was corrected from person cand-0258 to this work candidate; the person mention and work mention are now separately mapped. The card records the source-local original, not Guardi’s copy or an independently identified surviving version. Formal copying relation remains pending S6.",
        "process_ref": "S1-S4-full-book-2026-10-17",
    })

    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    for card_rel in (PERSON_CARD, WORK_CARD):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {card_rel}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    stats = sync.summarize_by_type(planned_candidates, planned_alignments)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    replacements = [
        ("| [实体候选](../tables/entity-candidates.csv) | 12,405 candidates（含直接关系端点候选 Luigi Pavini、Alessandro Farnese 公爵与 Paul Bonnefon） |",
         "| [实体候选](../tables/entity-candidates.csv) | 12,406 candidates（新增 Bassano’s Nativity 作品候选；含直接关系端点候选 Luigi Pavini、Alessandro Farnese 公爵与 Paul Bonnefon） |"),
        ("| [全书对齐](../tables/alignment.csv) | 12,631 条：12,405 条候选决定记录及 226 条外部身份记录；候选决定数见下表 |",
         "| [全书对齐](../tables/alignment.csv) | 12,632 条：12,406 条候选决定记录及 226 条外部身份记录；候选决定数见下表 |"),
        ("| [候选待办](../tables/candidate-backlog.csv) | 3条记录均已登记到KU，状态均为 completed；Paul Bonnefon编辑端点已完成S1/S3/S4登记，正式关系仍待S6 |",
         "| [候选待办](../tables/candidate-backlog.csv) | 4条记录均已登记到KU，状态均为 completed；新增 Bassano’s Nativity work endpoint；Paul Bonnefon编辑端点正式关系仍待S6 |"),
    ]
    for old, new in replacements:
        assert old in result_text, old
        result_text = result_text.replace(old, new, 1)

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S3–S4 类型边界修正：Jacopo Bassano 与 Nativity 作品端点（2026-10-17）\n\n"
        "S3 复核人物候选 `cand-0257`（B.csv#104）与 `cand-0258`（B.csv#105）：两条索引行的规范姓名均为 Jacopo Bassano，#105 的 ‘Nativity’ 是作品子项；人物组 `new-person:bassano-jacopo-0104694cf4` 保持不变，登记为一张人物卡。"
        f"发现 `st-chp10-p313-guardi-copied-bassano-nativity` 原将绘画名称 ‘Bassano’s Nativity’ 的 object 指向人物候选 `cand-0258`。现以新工作候选 `{WORK_CANDIDATE}` 区分对象，`m-s2-ch10-p313-0019` ‘Bassano’ 保留人物映射，`m-s2-ch10-p313-0020` ‘Nativity’ 改映射至作品；断言 object 与 mentioned_candidate_ids 同步更正。"
        "该 work 按 source-local new 身份经 candidate-backlog bl-0004 走 S1→S3→S4，登记为第二张 KU 卡。原文没有 Guardi 临摹件的具体版本/日期，故不另建副本对象。两条直接关系候选（Bassano 的艺术先例；Guardi 受命临摹此作品）留待 S6；本轮未写正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S3–S4 复核：Bassano 人物与 Nativity 作品分型（2026-10-17）\n\n"
        "索引 B.csv#104、#105 同指 Jacopo Bassano；人物两条候选共用一张 KU。p.313 的 “Bassano’s Nativity” 则为作品而非人物：新增 source-local work 候选并已登记，修正 S2 对象端点及提及映射。"
        "两张卡均保留临摹关系候选供 S6 审查；没有生成 Guardi 临摹件或正式关系。"
        f"S3 new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}；S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    person_card = make_card("雅各布·巴萨诺", "Jacopo Bassano", "person", PERSON_SOURCES, PERSON_BODY)
    work_card = make_card("巴萨诺《圣诞图》（S. Giorgio Maggiore）", "Bassano’s Nativity at S. Giorgio Maggiore", "work", WORK_SOURCES, WORK_BODY)

    if args.dry_run:
        print("Bassano person/work endpoint split and S4 dry-run passed")
        print("cand-0257 + cand-0258 -> one Jacopo Bassano person KU")
        print(f"{WORK_MENTION}: Nativity -> {WORK_CANDIDATE}; copied-work statement object corrected to the new work candidate")
        print("S1 backlog bl-0004 completes the source-local work candidate in this batch")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; candidates={len(candidates):,}->{len(planned_candidates):,}")
        print(f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}")
        print("no files changed")
        return 0

    for rel, content in ((PERSON_CARD, person_card), (WORK_CARD, work_card)):
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(CANDIDATES_PATH, candidate_fields, planned_candidates)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(BACKLOG_PATH, backlog_fields, planned_backlog)
    sync.write_csv(MENTIONS_PATH, mention_fields, planned_mentions)
    STATEMENTS_PATH.write_text("\n".join(planned_statement_lines) + "\n", encoding="utf-8-sig", newline="\n")
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Bassano person and Nativity work registered; manifest={len(planned_manifest)}; candidates={len(planned_candidates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
