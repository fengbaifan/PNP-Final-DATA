from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-16"
GROUP = "archive-group-4aa75cf1b8d7"
MEMBERS = ("cand-4359",)
KU_ID = "units/archives/pollak-italienische-kuenstlerbriefe-1913"
CARD_REL = "04-knowledge/units/archives/pollak-italienische-kuenstlerbriefe-1913.md"
NAME_ZH = "《巴洛克时期的意大利艺术家书信》"
NAME_EN = "Italian Artists’ Letters from the Baroque Period"
ORIGINAL_TITLE = "Italienische Künstlerbriefe aus der Barockzeit"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SOURCES = [
    {
        "chapter": "21", "page": "433", "file": "21_CHP-21Bibliography.md", "lines": "980–983",
        "quote": "Jahrbuch der Königlich-Preuszischen\nPollak, O.: ‘Italienische Künstlerbriefe aus der Barockzeit’ in\nKunstsammlungen,\n1913—Beiheft.",
        "summary": "第21章参考书目印刷页433列 O. Pollak 的 Italienische Künstlerbriefe aus der Barockzeit，标为 Jahrbuch der Königlich-Preuszischen Kunstsammlungen 的1913年 Beiheft。",
        "note": "书目条目以分行 OCR 显示，保留来源的 Preuszischen 拼写和 Beiheft 标记。",
    },
    {
        "chapter": "1", "page": "11", "file": "01_CHP-1_sec_ii.md", "lines": "189",
        "quote": "8 Pollak, 1913, p. 26. Letter from Lanfranco in Naples dated 14 July 1640.",
        "summary": "第1章 p.11 注6引用 Pollak 1913年版第26页，并把它作为 Lanfranco 1640年7月14日来信的刊载来源。",
        "note": "信件身份与刊载位置均按 Haskell 的注释转述；未查阅 Pollak 原文。",
    },
    {
        "chapter": "7", "page": "181", "file": "07_CHP-7_sec_i.md", "lines": "342",
        "quote": "4 Letter from Romanelli to Francesco Barberini of 6 July 1646—Pollak, 1913, p. 52.",
        "summary": "第7章 p.181 注4将 Romanelli 1646年7月6日致 Francesco Barberini 的信与 Pollak 1913年版第52页相连。",
        "note": "此处登记本书的引文指向，不表示原信或刊载文本已独立查看。",
    },
]


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def source_rows():
    rows = []
    for item in SOURCES:
        location = f"第{item['chapter']}章，印刷页{item['page']}；OCR L{item['lines']}"
        if item.get("note"):
            location += f"；{item['note']}"
        rows.append({
            "citation": BOOK_CITATION,
            "location": location,
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": f"lines {item['lines']}; print p. {item['page']}",
            },
        })
    return rows


def card_text():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "journal supplement",
        "evidence_status": "source_backed",
        "sources": source_rows(),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡登记 O. Pollak 的 *{ORIGINAL_TITLE}*，即《Jahrbuch der Königlich-Preuszischen Kunstsammlungen》1913年 Beiheft。Haskell 在第1、2、7章注释中引用该出版物不同页码，并将其作为若干艺术家书信的刊载来源；这只确认本书的书目指向，不表示已独立查阅 Pollak 的出版物或其所刊书信。中文标题为据原题所作的工作译名。

**English:** This card records O. Pollak’s *{ORIGINAL_TITLE}*, identified in the bibliography as a 1913 supplement to the *Jahrbuch der Königlich-Preuszischen Kunstsammlungen*. Notes in Chapters 1, 2, and 7 cite different pages of the publication and identify it as the printed source for several artists’ letters. This records Haskell’s bibliographic references; it does not indicate independent consultation of Pollak’s publication or the letters printed in it. The Chinese title is a descriptive working translation.

### 书目身份

- **原题名：** *{ORIGINAL_TITLE}*；第21章参考书目，印刷页433。
- **责任者：** O. Pollak；照录书目缩写。
- **刊物与版本：** *Jahrbuch der Königlich-Preuszischen Kunstsammlungen*，1913年 Beiheft（补编）。
- **本书引用位置：** Haskell 引 Pollak 1913年版 pp.5、26、33、41、44、52、60 等；这些是被引出版物的页码，不是 Haskell 本书的页码。具体被引页未独立查阅。

### 身份边界

S3 新组 `archive-group-4aa75cf1b8d7` 仅含出版物候选 `cand-4359`，不将它与刊载其中的个别信件候选合并。包括 `cand-4358`、`cand-4364`、`cand-4382`、`cand-4943`、`cand-7073` 和 `cand-3544` 的信件记录按各自对象保留；它们与此出版物的刊载关系仍须在 S6 核对。该补编也与 Pollak 的另一项著作 *Die Kunsttätigkeit unter Urban VIII*（候选 `cand-11421`）分开。未提供出版者或馆藏标识，不补造字段。

## 关系与证据

当前没有登记正式关系。S2 中八条关于 Haskell 引用该1913年补编的关系候选留待 S6；个别信件是否及如何刊载，应按各自的 S2 原文与端点裁决。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Pollak's 1913 Italian artists' letters supplement in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert all(cid in candidate_by_id for cid in MEMBERS)
    group_members = {
        cid for cid, row in decisions.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    for cid in MEMBERS:
        assert candidate_by_id[cid].get("suggested_type") == "archive"
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")

    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive"
        and ORIGINAL_TITLE.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )
    for item in SOURCES:
        text = " ".join((ROOT / "02-sources" / "02-Markdown" / item["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in text, (item["file"], item["quote"])

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert len(direct) == 10 and len(relations) == 8, (len(direct), len(relations))

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = card_text()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated archive card frontmatter is invalid"
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    process_append = (
        f"\n\n### S4 archive：Pollak 1913年艺术家书信补编身份组登记（{DATE}）\n\n"
        f"- `cand-4359` → `{GROUP}` → `{KU_ID}`；10条直接 S2 断言，其中8条出版物引用候选留待 S6。"
        "第21章 p.433 参考书目列出 O. Pollak 的题名、所在年鉴与1913年 Beiheft；第1、2、7章引用同一书目项的不同页码。"
        "仅登记补编出版物，不合并其所刊个别信件；cand-4358、cand-4364、cand-4382、cand-4943、cand-7073、cand-3544 保持各自信件对象。"
        "与 Pollak 的 *Die Kunsttätigkeit unter Urban VIII*（cand-11421）分开。未查阅补编原件，不新增正式关系或进行 S5 外部补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_process = process_text + process_append

    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; sources={len(SOURCES)}; "
            f"direct_statements={len(direct)}; relation_candidates_pending={len(relations)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
        )
        return 0

    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; direct_statements={len(direct)}; "
        f"relation_candidates_pending={len(relations)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
