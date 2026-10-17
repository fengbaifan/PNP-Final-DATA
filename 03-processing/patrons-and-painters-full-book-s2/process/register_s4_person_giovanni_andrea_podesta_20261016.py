from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-16"
KU_ID = "units/persons/giovanni-andrea-podesta"
CARD_REL = "04-knowledge/units/persons/giovanni-andrea-podesta.md"
CARD_PATH = ROOT / CARD_REL
GROUP = "new-person:andrea-podesta-070b483a9a"
MEMBERS = {"cand-5558", "cand-1964"}
NAME_ZH = "乔瓦尼·安德烈亚·波德斯塔"
NAME_EN = "Giovanni Andrea Podesta"
GETTY_URL = "https://www.getty.edu/vow/ULANFullDisplay?find=&nation=&role=&subjectid=500021868"
LOUVRE_URL = "https://arts-graphiques.louvre.fr/detail/artistes/0/2039-PODESTA-Giovanni-Andrea"
BACKUP_SUFFIX = ".bak-s4-giovanni-andrea-podesta-20261016"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


SOURCES = [
    {
        "citation": BOOK_CITATION,
        "location": "第4章，印刷页97；Markdown L30；PDF物理页4",
        "sentence_summary": "Haskell以Andrea Podesta称呼这位热那亚雕版师，并叙述其与Paolo Giordano II的联系及版画题献；此条保存书内用名和语境，不扩展作品作者关系。",
        "original_quotes": [{
            "source_span": "line 30; print p. 97; PDF physical p. 4",
            "text": "he was in touch with the Genoese engraver Andrea Podesta, who dedicated to him various prints of Bacchanals loosely based on the Aldobrandini Titians",
        }],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": "02-sources/02-Markdown/04_CHP-4_sec_i.md",
            "source_span": "line 30; print p. 97; PDF physical p. 4",
        },
    },
    {
        "citation": BOOK_CITATION,
        "location": "第4章，印刷页105；Markdown L82–83；PDF物理页16",
        "sentence_summary": "Haskell再次称Andrea Podesta为热那亚雕版师，并说他向Cassiano题献一幅取自Titian《维纳斯的崇拜》的版画；该句不识别版画制作者。",
        "original_quotes": [{
            "source_span": "lines 82–83; print p. 105; PDF physical p. 16",
            "text": "The Genoese engraver Andrea\nPodesta dedicated to him a print taken from Titian’s Worship of Venus-",
        }],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
            "source_span": "lines 82–83; print p. 105; PDF physical p. 16",
        },
    },
    {
        "citation": BOOK_CITATION,
        "location": "第7章，印刷页184注3；Markdown L356；PDF物理页18",
        "sentence_summary": "Haskell注3使用全名Giovanni Andrea Podesta，并转述其为1661年清单编制者之一及其与Mazarin的联系；de Cosnac条目和清单原件未独立查阅。",
        "original_quotes": [{
            "source_span": "line 356; print p. 184 n. 3; PDF physical p. 18",
            "text": "3 See the inventory of 1661 in de Cosnac, item 1240. Incidentally, among those who drew up this inventory was the Genoese painter and engraver Giovanni Andrea Podesta whose connection with Mazarin has not hitherto been noticed—see Blunt in Revue des Arts, 1958.",
        }],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
            "source_span": "line 356; print p. 184 n. 3; PDF physical p. 18",
        },
    },
    {
        "citation": BOOK_CITATION,
        "location": "全书索引，P.csv#165；索引页码97、105、184n",
        "sentence_summary": "索引以Podestà, Andrea为姓名主项，页码与第4章正文和第7章注3中的Podesta提及相符。",
        "original_quotes": [{"source_span": "P.csv#165", "text": "Podestà, Andrea"}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": "02-sources/03-Index/03-2-Index-CSV/P.csv",
            "source_span": "P.csv#165; indexed pages 97, 105, 184n",
        },
    },
    {
        "citation": f"Getty Vocabulary Program, Union List of Artist Names (ULAN), record 500021868. {GETTY_URL}. Accessed {DATE}.",
        "url": GETTY_URL,
        "accessed_date": DATE,
        "location": "ULAN 500021868；规范名及别名、Genoese国别标识、职业角色",
        "sentence_summary": "Getty ULAN prefers Podesta, Giovanni Andrea, lists Podestà, Andrea as an alternate name, and records Genoese identity and painter/printmaker/engraver/etcher roles. Its date summaries vary; this card does not adopt dates.",
        "original_quotes": [],
    },
    {
        "citation": f"Musée du Louvre, Département des Arts graphiques, artist authority PODESTA Giovanni Andrea. {LOUVRE_URL}. Accessed {DATE}.",
        "url": LOUVRE_URL,
        "accessed_date": DATE,
        "location": "卢浮宫图像艺术部艺术家权威记录；规范名、同义名及职业角色",
        "sentence_summary": "卢浮宫记录以PODESTA Giovanni Andrea为标题，列Podesta Andrea为同义名，并称其为画家和雕版师；该卡只采用姓名与职业身份信息。",
        "original_quotes": [],
    },
]


def normalized(text: str) -> str:
    return " ".join(text.split())


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": SOURCES,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p97 = "[第4章 p.97](../../../02-sources/02-Markdown/04_CHP-4_sec_i.md)（L30）"
    p105 = "[第4章 p.105](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md)（L82–83）"
    p184 = "[第7章 p.184注3](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L356）"
    index = "[全书索引 P.csv#165](../../../02-sources/03-Index/03-2-Index-CSV/P.csv)"
    getty = f"[Getty ULAN 500021868]({GETTY_URL})"
    louvre = f"[卢浮宫艺术家权威记录]({LOUVRE_URL})"
    body = f"""## 内容

### 描述

**中文：** 本卡将第4章所称 Andrea Podesta 与第7章注3所写全名 Giovanni Andrea Podesta 记录为同一人物。Haskell在第4章称其为热那亚雕版师；第7章称其为热那亚画家和雕版师。Getty ULAN 与卢浮宫艺术家权威记录均列出与书内形式相符的姓名变体。中文显示名为项目工作译名。有关1661年清单及其与Mazarin联系的内容只保留为Haskell转述，de Cosnac条目及清单原件未独立查阅；本卡不据此建立正式关系边。{p97} {p105} {p184}

**English:** This card treats the Chapter 4 form Andrea Podesta and the full name Giovanni Andrea Podesta in Chapter 7 note 3 as the same person. Haskell calls him a Genoese engraver in Chapter 4 and a Genoese painter and engraver in Chapter 7. Getty ULAN and the Louvre artist authority both list name variants that match the forms in the book. The Chinese display name is a project working transliteration. The reported role in the 1661 inventory and the reported connection with Mazarin remain attributed to Haskell; de Cosnac’s item and the inventory itself have not been independently consulted, and this card creates no formal relation edge. {p97} {p105} {p184}

### 姓名与别名

| 字段 | 值 | 证据 |
|---|---|---|
| 规范全名 | Giovanni Andrea Podesta | S3；S5；S6；{p184}；{getty}；{louvre} |
| 书内称名 | Andrea Podesta；Andrea Podestà | S1–S2；S4；{p97}；{p105}；{index} |
| 外部权威姓名变体 | Podestà, Andrea；Podesta Andrea | S5–S6；{getty}；{louvre} |

### 身份信息

| 字段 | 值 | 证据 |
|---|---|---|
| 书内职业称谓 | 热那亚雕版师；第7章亦称画家 | S1–S3；{p97}；{p105}；{p184} |
| 外部权威职业称谓 | 画家、雕版师／版画制作者、蚀刻师 | S5–S6；{getty}；{louvre} |

### 本章相关内容

- 第4章p.97与p.105均以Andrea Podesta称呼该人物；后一处所述版画题献没有识别该版画的制作者。{p97} {p105}
- 第7章p.184注3以全名Giovanni Andrea Podesta转述其参与拟制1661年清单，并称他与Mazarin的联系此前未受注意；原清单及所引Blunt文章均未独立查阅。{p184}
- Getty ULAN所列日期摘要与卢浮宫记录的日期范围不一致，本卡不登记生卒年。{getty} {louvre}

## 关系与证据

### 身份与外部链接

| 字段 | 值／链接 | 状态与范围 | 证据 |
|---|---|---|---|
| Getty ULAN | {getty} | 支持规范名、`Podestà, Andrea`别名及职业角色；不验证Haskell的关系叙述 | S5 |
| 卢浮宫艺术家权威记录 | {louvre} | 支持`Podesta Andrea`同义名及职业角色；记录注明页面内容可能不代表最新研究状态 | S6 |

### 关系记录

当前没有登记正式关系。第4章关于交往和版画题献、第7章关于清单编制者及Mazarin联系的S2关系候选，继续留待S6逐条审查。{p97} {p105} {p184}
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Podesta cross-chapter person identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignment = sync.read_csv(ALIGNMENT)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    primary_by_id = {
        row["candidate_id"]: row for row in alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    if len(manifest) != 1324 or any(row.get("ku_id") == KU_ID for row in manifest):
        raise SystemExit("Unexpected manifest baseline or the Podesta person KU already exists.")
    for cid in MEMBERS:
        row = primary_by_id.get(cid)
        if not row or row.get("decision") != "new" or row.get("ku_id"):
            raise SystemExit(f"{cid} is no longer an unmapped S3-new group member.")
        if sync.get_group(row.get("resolution_note", "")) != GROUP:
            raise SystemExit(f"{cid} no longer belongs to {GROUP}.")
        if candidate_by_id[cid].get("suggested_type") != "person":
            raise SystemExit(f"{cid} no longer has person type.")
    group_members = {
        row["candidate_id"] for row in alignment
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    if group_members != MEMBERS:
        raise SystemExit(f"Unexpected membership for {GROUP}: {sorted(group_members)}")
    identity_rows = [
        row for row in alignment
        if row.get("candidate_id") == "cand-5558" and row.get("external_id") in {GETTY_URL, LOUVRE_URL}
    ]
    if len(identity_rows) != 2 or any(row.get("decision") != "new" for row in identity_rows):
        raise SystemExit("Expected the two S3 external identity rows for Getty ULAN and the Louvre.")
    if CARD_PATH.exists():
        raise SystemExit(f"S4 card already exists: {CARD_REL}")

    source_quotes = {
        "02-sources/02-Markdown/04_CHP-4_sec_i.md": [SOURCES[0]["original_quotes"][0]["text"]],
        "02-sources/02-Markdown/04_CHP-4_sec_ii.md": [SOURCES[1]["original_quotes"][0]["text"]],
        "02-sources/02-Markdown/07_CHP-7_sec_i.md": [SOURCES[2]["original_quotes"][0]["text"]],
        "02-sources/03-Index/03-2-Index-CSV/P.csv": ['"Podestà, Andrea",,,,"97, 105, 184n"'],
    }
    for source_file, quotes in source_quotes.items():
        text = normalized((ROOT / source_file).read_text(encoding="utf-8-sig"))
        for quote in quotes:
            if normalized(quote) not in text:
                raise SystemExit(f"Source quote no longer matches {source_file}: {quote}")

    planned_alignment = [dict(row) for row in alignment]
    for row in planned_alignment:
        if row.get("candidate_id") in MEMBERS and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    planned_manifest.sort(key=lambda row: row["ku_id"])
    accepted_text = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))
    card = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    if not frontmatter_match:
        raise SystemExit("Generated card frontmatter could not be parsed.")
    card_frontmatter = yaml.safe_load(frontmatter_match.group(1))
    if card_frontmatter.get("type") != "person" or len(card_frontmatter.get("sources", [])) != 6:
        raise SystemExit("Generated card frontmatter failed validation.")

    statements = [
        json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    related = [
        row for row in statements
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    pending_relation_candidates = sum(bool(row.get("qualifiers", {}).get("relation_candidate")) for row in related)
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    detail = (
        f"### S4 person：Giovanni Andrea Podesta 跨章身份组登记（{DATE}）\n\n"
        f"- `cand-5558`（第4章正文人物候选）与 `cand-1964`（P.csv#165，页码97、105、184n）共用S3身份组 `{GROUP}`，现共同映射至 `units/persons/giovanni-andrea-podesta`。卡片以第7章全名为规范名；Getty ULAN与卢浮宫权威记录支持书内别名。两条权威记录的日期范围不一致，故本卡不录生卒年。\n"
        f"- 第4章关于交往与版画题献、第7章关于1661年清单编制者及Mazarin联系的关系候选继续待S6；清单与Blunt文章未独立查阅。本次不写入正式关系，也不将版画题献解释为版画创作。涉及候选的S2陈述共{len(related)}条，其中{pending_relation_candidates}条为关系候选，仍由原statement记录承载。\n"
        f"- 新增1张person卡、1条manifest、2条候选KU映射及accepted路径；S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person为{sync.fmt(stats['person']['registered_groups'])}组已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员待登记；KU总数{len(planned_manifest)}。字段事实与外部来源由 `build_field_facts.py` 后续预检登记。\n\n"
    )
    marker = "## 未解决项与交接限制"
    if result_text.count(marker) != 1:
        raise SystemExit("Could not locate result insertion point.")
    result_text = result_text.replace(marker, detail + marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    heading = f"### S4 person：Giovanni Andrea Podesta {GROUP}"
    if heading in process_text:
        raise SystemExit("Podesta S4 process record already exists.")
    process_text += (
        f"\n\n{heading}（{DATE}）\n\n"
        f"- `cand-5558`与`cand-1964`共同映射至`{KU_ID}`，索引及正文候选仍保留各自来源定位。人物卡以第7章p.184注3的全名为规范名，采用第4章p.97和p.105的姓名变体；中文名为工作音译。\n"
        "- Getty ULAN 500021868及卢浮宫图像艺术部权威记录支持姓名变体与职业识别。二者日期摘要不同，故未录生卒年。Haskell关于1661年清单及Mazarin联系的叙述仅作为有来源归属的书内说法；de Cosnac item 1240、原清单和Blunt文章未独立查阅。\n"
        f"- 卡片保留双语描述、书内来源定位和两条外部身份链接；涉及该人物的{len(related)}条S2陈述中，{pending_relation_candidates}条关系候选仍待S6逐条核查。本轮不新增正式关系边。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条映射；person为{sync.fmt(stats['person']['registered_groups'])}组已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员待登记；KU总数{len(planned_manifest)}。\n"
    )

    updates = {
        ALIGNMENT: None,
        MANIFEST: None,
        ACCEPTED: accepted_text,
        PROCESS: process_text,
        RESULT: result_text,
    }
    if args.dry_run:
        print(
            f"dry-run passed: group={GROUP}; candidates={','.join(sorted(MEMBERS))}; card={KU_ID}; "
            f"related_statements={len(related)}; relation_candidates_pending={pending_relation_candidates}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
        )
        return 0

    target_files = [ALIGNMENT, MANIFEST, ACCEPTED, PROCESS, RESULT]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in target_files]
    if any(path.exists() for path in backups):
        raise SystemExit("A Podesta S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(target_files, backups, strict=True):
        shutil.copy2(original, backup)
    CARD_PATH.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(ALIGNMENT, alignment_fields, planned_alignment)
    sync.write_csv(MANIFEST, manifest_fields, planned_manifest)
    ACCEPTED.write_text(accepted_text, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {','.join(sorted(MEMBERS))} -> {KU_ID}; relation_candidates_pending={pending_relation_candidates}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"recovery_backups={len(target_files)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
