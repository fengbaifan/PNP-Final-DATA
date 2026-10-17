from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
BACKLOG = TABLES / "candidate-backlog.csv"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"

DATE = "2026-10-16"
BACKLOG_ID = "bl-0003"
CANDIDATE_ID = "cand-12427"
GROUP = "new-person:paul-bonnefon-1861-1922"
KU_ID = "units/persons/paul-bonnefon"
CARD_REL = "04-knowledge/units/persons/paul-bonnefon.md"
CARD_PATH = ROOT / CARD_REL
SOURCE_FILE = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
SOURCE_REF = "chp-21:21_CHP-21Bibliography:l243-293#L254"
STATEMENT_ID = "st-chp21-bib-l243-293-entry-07"
BNF_URL = "https://catalogue.bnf.fr/ark:/12148/cb12115372q"
BNF_CITATION = f"BnF Catalogue général, notice de personne FRBNF12115372. {BNF_URL}. Accessed {DATE}."
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BACKUP_SUFFIX = ".bak-s1-s3-s4-paul-bonnefon-20261016"

QUOTE = (
    "Brienne, Louis-Henri de Loménie Comte de: Mémoires, publiés par Paul Bonnefon, 3 vols., "
    "Paris 1916-19."
)


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第21章书末参考书目，印刷页417；Markdown L254–255",
            "sentence_summary": "Haskell书目列出Brienne《Mémoires》，注明Paul Bonnefon为责任者、三卷本及Paris 1916–19；该书目提供本轮人物端点的书内身份锚点。",
            "original_quotes": [{
                "source_span": "lines 254–255; printed bibliography p. 417",
                "text": QUOTE,
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_FILE,
                "source_span": "lines 254–255; printed bibliography p. 417",
            },
        },
        {
            "citation": BNF_CITATION,
            "url": BNF_URL,
            "accessed_date": DATE,
            "location": "BnF person authority FRBNF12115372；规范姓名、生卒年月日、责任者身份及职业职务",
            "sentence_summary": "BnF规范记录将人物列为Bonnefon, Paul（1861–1922），标注其为法国作者，并记载其曾任Arsenal图书馆馆员及法国文学协会秘书长。",
            "original_quotes": [],
        },
    ]
    frontmatter = {
        "title": "保罗·博纳丰（Paul Bonnefon）",
        "name_en": "Paul Bonnefon",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    bibliography = "[第21章书目 p.417](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L254–255）"
    bnf = f"[BnF人物权威记录 FRBNF12115372]({BNF_URL})"
    body = f"""## 内容

### 描述

**中文：** 本卡登记保罗·博纳丰（Paul Bonnefon）。BnF人物规范记录将其识别为1861–1922年的法国作者，并记载他曾任Arsenal图书馆馆员及法国文学协会秘书长。Haskell第21章书目以“publiés par Paul Bonnefon”列出其与布里埃纳《Mémoires》三卷本的责任关系；此处保留为书目中的编辑责任表述，正式编辑关系留待S6逐项审查。中文名为项目工作音译。{bibliography} {bnf}

**English:** This card records Paul Bonnefon (1861–1922), whom the BnF person authority identifies as a French author, conservator at the Bibliothèque de l'Arsenal, and secretary-general of the Société littéraire de France. Haskell’s Chapter 21 bibliography credits “publiés par Paul Bonnefon” in connection with the three-volume *Mémoires* of Brienne; this remains a bibliographic responsibility statement, while a formal editor relation is reserved for S6 review. The Chinese name is a project working transliteration. {bibliography} {bnf}

### 姓名与基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Paul Bonnefon | S1–S2；{bibliography}；{bnf} |
| 出生日期 | 1861年9月9日 | S2；{bnf} |
| 去世日期 | 1922年4月11日 | S2；{bnf} |
| 作者身份 | Auteur（作者） | S2；{bnf} |

### 职业与职务

| 字段 | 值 | 证据 |
|---|---|---|
| 职业职务 | Conservateur à la Bibliothèque de l'Arsenal（Arsenal图书馆馆员） | S2；{bnf} |
| 机构职务 | Secrétaire général de la Société littéraire de France（法国文学协会秘书长） | S2；{bnf} |

## 关系与证据

### 身份与外部链接

| 字段 | 值／链接 | 状态与范围 | 证据 |
|---|---|---|---|
| BnF人物权威记录 | {bnf} | 支持姓名、生卒年月日及人物身份；不单独核验Haskell书目所述责任关系 | S2 |

### 关系记录

当前没有登记正式关系。Haskell书目将Bonnefon列为Brienne《Mémoires》的编辑责任者；该来源陈述对应的正式关系留待S6审查。{bibliography}
"""
    return f"---\n{fm}---\n\n{body}"


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    if any(line.strip() == f"- {CARD_REL}" for line in lines):
        raise SystemExit("Accepted path already exists.")
    insert_at = next(
        (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def replace_line(text: str, prefix: str, replacement: str, label: str) -> str:
    lines = text.splitlines()
    matches = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(matches) != 1:
        raise SystemExit(f"Could not uniquely update {label}; matches={len(matches)}.")
    lines[matches[0]] = replacement
    return "\n".join(lines) + "\n"


def source_check() -> None:
    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    if " ".join(QUOTE.split()) not in source_text:
        raise SystemExit("Haskell bibliography source anchor changed.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Drain Paul Bonnefon from S1 through S3 and S4.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(CANDIDATES)
    alignment_fields, alignment = sync.read_csv(ALIGNMENT)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    backlog_fields, backlog = sync.read_csv(BACKLOG)
    backlog_row = next((row for row in backlog if row.get("backlog_id") == BACKLOG_ID), None)
    if not backlog_row or backlog_row.get("status") != "pending" or backlog_row.get("candidate_id") or backlog_row.get("ku_id"):
        raise SystemExit("Backlog bl-0003 is no longer pending at the expected baseline.")
    if backlog_row.get("source_ref") != SOURCE_REF or backlog_row.get("statement_id") != STATEMENT_ID:
        raise SystemExit("Backlog source anchor changed.")
    if len(candidates) != 12404 or len(alignment) != 12628 or len(manifest) != 1328:
        raise SystemExit("Candidate/alignment/manifest baseline changed; inspect before applying.")
    if any(row.get("candidate_id") == CANDIDATE_ID for row in candidates):
        raise SystemExit(f"{CANDIDATE_ID} already exists.")
    if any(row.get("candidate_id") == CANDIDATE_ID for row in alignment):
        raise SystemExit(f"Alignment already contains {CANDIDATE_ID}.")
    if any(row.get("ku_id") == KU_ID for row in manifest) or CARD_PATH.exists():
        raise SystemExit("The Paul Bonnefon KU already exists.")
    if any(
        row.get("type") == "person"
        and "bonnefon" in f"{row.get('canonical_name', '')} {row.get('name_en', '')} {row.get('card_path', '')}".casefold()
        for row in manifest
    ):
        raise SystemExit("A possible same-person KU exists in the manifest.")
    if any(sync.get_group(row.get("resolution_note", "")) == GROUP for row in alignment):
        raise SystemExit("The planned person identity group already exists.")
    if any(row.get("candidate_id") == CANDIDATE_ID and row.get("external_id") == BNF_URL for row in alignment):
        raise SystemExit("The BnF authority identity row already exists.")
    source_check()

    candidate = {
        "candidate_id": CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Paul Bonnefon",
        "index_page_range": "",
        "suggested_type": "person",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell’s Chapter 21 bibliography names Paul Bonnefon in the responsibility statement for Brienne’s three-volume Mémoires edition, Paris 1916–19. This candidate represents the named person endpoint; the formal editor relation remains for S6.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": SOURCE_REF,
    }
    primary_alignment_id = max(
        int(row["alignment_id"].removeprefix("aln-"))
        for row in alignment
        if row.get("alignment_id", "").startswith("aln-") and row["alignment_id"][4:].isdigit()
    ) + 1
    external_alignment_id = primary_alignment_id + 1
    primary_note = (
        f"source_ref={SOURCE_REF}; candidate_backlog={BACKLOG_ID}; statement={STATEMENT_ID}; group={GROUP}; "
        "S3 identity: the source bibliography names Paul Bonnefon in the responsibility statement for the three-volume Mémoires; "
        "BnF person authority FRBNF12115372 identifies Bonnefon, Paul (1861-1922), author, and records his Arsenal Library and Société littéraire de France positions. "
        "BnF publication record FRBNF34019339 identifies the Brienne Mémoires edition edited by Paul Bonnefon. "
        "No matching person KU exists; decide new. This resolves the person endpoint identity only; the editor relation remains pending S6. "
        f"S4 registration: mapped {GROUP} to {KU_ID}."
    )
    primary = {
        "alignment_id": f"aln-{primary_alignment_id}",
        "candidate_id": CANDIDATE_ID,
        "ku_id": KU_ID,
        "external_source": "",
        "external_id": "",
        "decision": "new",
        "accessed_date": "",
        "process_ref": "S3-S4-full-book-2026-10-16",
        "legacy_ku_id": "",
        "resolution_note": primary_note,
    }
    external = {
        "alignment_id": f"aln-{external_alignment_id}",
        "candidate_id": CANDIDATE_ID,
        "ku_id": "",
        "external_source": "BnF Catalogue général",
        "external_id": BNF_URL,
        "decision": "new",
        "accessed_date": DATE,
        "process_ref": "S3-full-book-2026-10-16",
        "legacy_ku_id": "",
        "resolution_note": (
            "Identity only: BnF person authority FRBNF12115372 identifies Bonnefon, Paul (1861-1922), "
            "lists him as an author, and records his positions at the Bibliothèque de l'Arsenal and Société littéraire de France. "
            "It supports the person identity, not by itself the editor relation to the Brienne Mémoires."
        ),
    }
    planned_candidates = list(candidates) + [candidate]
    planned_alignment = list(alignment) + [primary, external]
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "保罗·博纳丰",
        "name_en": "Paul Bonnefon",
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    planned_manifest.sort(key=lambda row: row["ku_id"])

    planned_backlog = [dict(row) for row in backlog]
    target_backlog = next(row for row in planned_backlog if row.get("backlog_id") == BACKLOG_ID)
    target_backlog.update({
        "status": "completed",
        "candidate_id": CANDIDATE_ID,
        "ku_id": KU_ID,
        "decision_note": (
            "Prior rationale retained: no matching person KU or S3 candidate was found when bl-0003 was queued. "
            f"S1 candidate {CANDIDATE_ID} was created from the cited bibliography line; S3 assigns {GROUP} as a new person identity, "
            "supported by BnF person authority FRBNF12115372 and the existing BnF publication record FRBNF34019339. "
            f"S4 registered the endpoint as {KU_ID}. Endpoint registration is complete; the formal editor relation to Brienne's Mémoires remains pending S6."
        ),
        "process_ref": "S3-S4-full-book-2026-10-16",
    })
    accepted_text = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))
    card = make_card()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    if not match:
        raise SystemExit("Generated card frontmatter failed to parse.")
    parsed = yaml.safe_load(match.group(1))
    if parsed.get("type") != "person" or len(parsed.get("sources", [])) != 2:
        raise SystemExit("Generated person card failed frontmatter validation.")

    stats = sync.summarize_by_type(planned_candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"),
        stats,
        totals,
        len(planned_manifest),
    )
    result_text = replace_line(
        result_text,
        "| [实体候选](",
        "| [实体候选](../tables/entity-candidates.csv) | 12,405 candidates（含直接关系端点候选 Luigi Pavini、Alessandro Farnese 公爵与 Paul Bonnefon） |",
        "candidate artifact count",
    )
    result_text = replace_line(
        result_text,
        "| [全书对齐](",
        "| [全书对齐](../tables/alignment.csv) | 12,630 条：12,405 条候选决定记录及 225 条外部身份记录；候选决定数见下表 |",
        "alignment artifact count",
    )
    result_text = replace_line(
        result_text,
        "| [候选待办](",
        "| [候选待办](../tables/candidate-backlog.csv) | 3条记录均已登记到KU，状态均为 completed；Paul Bonnefon编辑端点已完成S1/S3/S4登记，正式关系仍待S6 |",
        "candidate backlog status",
    )
    result_text = replace_line(
        result_text,
        "- 书目编者Paul Bonnefon尚无对应person KU",
        "- 书目编者Paul Bonnefon已通过 bl-0003 完成S1候选、S3身份裁决及S4 KU登记；人物身份由BnF规范记录支持，正式编辑关系仍留待S6。",
        "Brienne editor endpoint status",
    )
    result_text = result_text.replace(
        "审计警告中的4,639条未登记new alignment行包含18条未登记外部身份记录；候选决定自身的S4待登记映射为4,621条、分属4,531组。",
        "审计警告中的4,640条未登记new alignment行包含19条未登记外部身份记录；候选决定自身的S4待登记映射为4,621条、分属4,531组。",
        1,
    )
    if "19条未登记外部身份记录" not in result_text:
        raise SystemExit("Could not refresh current S4 audit counts.")

    detail = (
        f"### S3 person：Paul Bonnefon 直接关系端点身份裁决（{DATE}）\n\n"
        f"- backlog {BACKLOG_ID} 源于第21章书目候选 {STATEMENT_ID}，source_ref为 {SOURCE_REF}。书目原文将 Paul Bonnefon 列入 Brienne《Mémoires》三卷本的 publiés par 责任表述；既有 archive KU 与BnF书目记录FRBNF34019339对应同一出版物。\n"
        f"- 新增S1人物候选 {CANDIDATE_ID}。BnF人物权威 FRBNF12115372（{BNF_URL}）识别为Bonnefon, Paul（1861–1922），并记录其作者身份和Arsenal图书馆、法国文学协会职务；当前manifest无同一人物KU，故裁为 {GROUP} / new。该裁决只确认人物端点，不将编辑责任自动写成S6正式边。\n"
        f"- 增加候选决定行 aln-{primary_alignment_id} 与BnF人物身份行 aln-{external_alignment_id}；原backlog理由保留在完成说明中。\n\n"
        f"### S4 person：Paul Bonnefon 人物组登记（{DATE}）\n\n"
        f"- {CANDIDATE_ID} 映射至 {KU_ID}；新增person卡、manifest、accepted路径及候选KU映射。卡片记录双语名称与描述、BnF规范姓名、生卒年月日、作者身份及有据职务；中文名为项目工作音译。\n"
        f"- backlog {BACKLOG_ID} 更新为 completed，只表示身份端点已登记。与Brienne《Mémoires》的正式编辑关系仍待S6逐条审查；未新增relations.csv边。\n"
        f"- S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person为{sync.fmt(stats['person']['registered_groups'])}组已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员待登记；KU总数{len(planned_manifest)}。字段事实由 build_field_facts.py 预检登记。\n\n"
    )
    if result_text.count("## 未解决项与交接限制") != 1:
        raise SystemExit("Could not locate result insertion point.")
    result_text = result_text.replace("## 未解决项与交接限制", detail + "## 未解决项与交接限制", 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_text = replace_line(
        process_text,
        "- Paul Bonnefon由第21章书目记为编者但尚无person KU",
        f"- Paul Bonnefon由第21章书目记为编者；backlog {BACKLOG_ID} 后续已按S1→S3→S4处理，候选 {CANDIDATE_ID} 映射至 {KU_ID}，端点登记完成。正式编辑关系仍待S6。",
        "Brienne editor endpoint process status",
    )
    process_text += (
        f"\n\n### S3 person：Paul Bonnefon 直接关系端点身份裁决（{DATE}）\n\n"
        f"- backlog {BACKLOG_ID} 定位第21章书目候选 {STATEMENT_ID}，source_ref {SOURCE_REF}。原文书目列Brienne, Louis-Henri de Loménie Comte de: *Mémoires*, publiés par Paul Bonnefon, 3 vols., Paris 1916–19。既有书籍KU为 units/archives/brienne-memoires-1916-1919；BnF出版物记录FRBNF34019339确认同一版本并列Paul Bonnefon为编辑责任者。\n"
        f"- 新增S1人物候选 {CANDIDATE_ID}。BnF人物权威FRBNF12115372（{BNF_URL}）将规范名列为Bonnefon, Paul（1861–1922），记录作者责任、Arsenal图书馆馆员和法国文学协会秘书长身份；manifest与person卡中未发现同一人。候选裁为 {GROUP} / new，只解决端点身份，不把书目责任形式自动转为S6正式关系。\n"
        f"- 新增S3候选行 aln-{primary_alignment_id} 和BnF人物权威行 aln-{external_alignment_id}。旧backlog所述“没有匹配person KU或S3候选”作为裁决前状态保留在backlog完成说明中。\n\n"
        f"### S4 person：Paul Bonnefon 人物组登记（{DATE}）\n\n"
        f"- {CANDIDATE_ID} → {GROUP} → {KU_ID}。新增双语person卡、manifest、accepted路径和候选KU映射；字段表以Haskell书目与BnF人物权威为依据，不扩写超出所录证据的生平。\n"
        f"- backlog {BACKLOG_ID} 现为 completed，表示S1候选、S3身份与S4端点登记完成；与Brienne《Mémoires》的正式编辑关系仍留待S6，未新增relations.csv边。\n"
        f"- S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员。字段事实待build_field_facts.py预检。\n"
    )

    targets = [CANDIDATES, ALIGNMENT, MANIFEST, BACKLOG, ACCEPTED, PROCESS, RESULT]
    backup_paths = [path.with_name(path.name + BACKUP_SUFFIX) for path in targets]
    if any(path.exists() for path in backup_paths):
        raise SystemExit("A Paul Bonnefon S1-S4 recovery copy already exists.")
    if args.dry_run:
        print(f"dry-run passed: {CANDIDATE_ID}->{GROUP}->{KU_ID}; primary=aln-{primary_alignment_id}; BnF=aln-{external_alignment_id}")
        print(f"candidates={len(candidates)}->{len(planned_candidates)}; alignment={len(alignment)}->{len(planned_alignment)}; manifest={len(manifest)}->{len(planned_manifest)}")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; backlog bl-0003=pending->completed")
        return 0

    for original, backup in zip(targets, backup_paths, strict=True):
        shutil.copy2(original, backup)
    sync.write_csv(CANDIDATES, candidate_fields, planned_candidates)
    sync.write_csv(ALIGNMENT, alignment_fields, planned_alignment)
    sync.write_csv(MANIFEST, manifest_fields, planned_manifest)
    sync.write_csv(BACKLOG, backlog_fields, planned_backlog)
    ACCEPTED.write_text(accepted_text, encoding="utf-8-sig", newline="\n")
    CARD_PATH.write_text(card, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: {CANDIDATE_ID}->{GROUP}->{KU_ID}; primary=aln-{primary_alignment_id}; BnF=aln-{external_alignment_id}")
    print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
