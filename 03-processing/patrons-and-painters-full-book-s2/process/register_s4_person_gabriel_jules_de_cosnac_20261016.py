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
CID = "cand-7086"
GROUP = "new-person:comte-cosnac-de-gabriel-jules-5d54b2a724"
KU_ID = "units/persons/gabriel-jules-de-cosnac"
CARD_REL = "04-knowledge/units/persons/gabriel-jules-de-cosnac.md"
CARD_PATH = ROOT / CARD_REL
BNF_URL = "https://catalogue.bnf.fr/ark:/12148/cb12982918p"
BACKUP_SUFFIX = ".bak-s4-gabriel-jules-de-cosnac-20261016"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


SOURCES = [
    {
        "citation": BOOK_CITATION,
        "location": "第21章书末参考书目，印刷页420；Markdown L380",
        "sentence_summary": "Haskell书目将Les richesses du Palais Mazarin列于Comte Gabriel-Jules de Cosnac名下，出版项为Paris 1885；该书目只记录书内责任者形式。",
        "original_quotes": [{
            "source_span": "line 380; bibliography p. 420",
            "text": "Cosnac, Comte Gabriel-Jules de: Les richesses du Palais Mazarin, Paris 1885.",
        }],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
            "source_span": "line 380; printed bibliography p. 420",
        },
    },
    {
        "citation": f"BnF Catalogue général, notice de personne FRBNF12982918. {BNF_URL}. Accessed {DATE}.",
        "url": BNF_URL,
        "accessed_date": DATE,
        "location": "BnF authority record FRBNF12982918；规范名、异名、头衔、职业、生卒年月日及地点",
        "sentence_summary": "BnF人物权威记录将Gabriel-Jules de Cosnac列为规范名，生卒年为1819–1893；记录称其为伯爵、历史学家，并提供生卒年月日和地点，列Jules de Cosnac为被拒姓名形式。",
        "original_quotes": [],
    },
]


def make_card() -> str:
    frontmatter = {
        "title": "加布里埃尔-朱尔·德·科斯纳克（Gabriel-Jules de Cosnac）",
        "name_en": "Gabriel-Jules de Cosnac",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": SOURCES,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    bib = "[第21章书目 p.420](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L380）"
    bnf = f"[BnF人物权威记录 FRBNF12982918]({BNF_URL})"
    body = f"""## 内容

### 描述

**中文：** 本卡登记加布里埃尔-朱尔·德·科斯纳克（Gabriel-Jules de Cosnac，伯爵、历史学家）。Haskell第21章书目以“Comte Gabriel-Jules de Cosnac”列出《Les richesses du Palais Mazarin》（Paris, 1885）的责任者；BnF人物权威记录给出其规范名、生卒年月日及地点，并列出“Jules de Cosnac”为被拒姓名形式。中文名为项目工作音译。该书的具体作者关系和书内引用关系留待S6，不由书目形式直接写成正式边。{bib} {bnf}

**English:** This card records Gabriel-Jules de Cosnac (Comte; historian). Haskell’s Chapter 21 bibliography lists “Comte Gabriel-Jules de Cosnac” as the responsibility form for *Les richesses du Palais Mazarin* (Paris, 1885). The BnF person authority record gives the authorized name, full life dates and places, and lists “Jules de Cosnac” as a rejected form. The Chinese name is a project working transliteration. The specific author relation to the book and its cited passages remains for S6 review; the bibliographic form is not turned directly into a formal edge. {bib} {bnf}

### 姓名与称号

| 字段 | 值 | 证据 |
|---|---|---|
| 规范名称 | Gabriel-Jules de Cosnac | S1–S2；{bib}；{bnf} |
| 异名形式 | Jules de Cosnac | S2；{bnf} |
| 伯爵称号 | Comte de Cosnac | S1–S2；{bib}；{bnf} |

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 职业身份 | Historian（历史学家） | S2；{bnf} |
| 出生日期 | 1819年4月13日 | S2；{bnf} |
| 去世日期 | 1893年4月19日 | S2；{bnf} |
| 出生地 | Clermont | S2；{bnf} |
| 去世地 | Paris | S2；{bnf} |

## 关系与证据

### 身份与外部链接

| 字段 | 值／链接 | 状态与范围 | 证据 |
|---|---|---|---|
| BnF人物权威记录 | {bnf} | 支持人物身份、姓名、头衔、生卒日期与地点 | S2 |

### 关系记录

当前没有登记正式关系。Haskell书目将其列为《Les richesses du Palais Mazarin》的责任者；与该刊本及其所引1661年清单的正式关系留待S6逐项审查。{bib} {bnf}
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
    parser = argparse.ArgumentParser(description="Register Gabriel-Jules de Cosnac in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidates_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignment = sync.read_csv(ALIGNMENT)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate = next((row for row in candidates if row.get("candidate_id") == CID), None)
    primary = [row for row in alignment if row.get("candidate_id") == CID and not row.get("external_source")]
    if not candidate or candidate.get("suggested_type") != "person" or candidate.get("canonical_name") != "Comte Gabriel-Jules de Cosnac":
        raise SystemExit("Unexpected S1 candidate record for de Cosnac.")
    if len(primary) != 1 or primary[0].get("decision") != "new" or primary[0].get("ku_id") or sync.get_group(primary[0].get("resolution_note", "")) != GROUP:
        raise SystemExit("cand-7086 is no longer an unmapped new member of the expected person group.")
    if any(row.get("ku_id") == KU_ID for row in manifest) or len(manifest) != 1325 or CARD_PATH.exists():
        raise SystemExit("Unexpected manifest baseline or de Cosnac person KU already exists.")
    if any(row.get("candidate_id") == CID and row.get("external_id") == BNF_URL for row in alignment):
        raise SystemExit("The BnF person identity row already exists.")
    if sync.get_group(primary[0].get("resolution_note", "")) != GROUP:
        raise SystemExit("The candidate identity group changed.")
    source_text = (ROOT / "02-sources/02-Markdown/21_CHP-21Bibliography.md").read_text(encoding="utf-8-sig")
    if "Cosnac, Comte Gabriel-Jules de: Les richesses du Palais Mazarin, Paris 1885." not in source_text:
        raise SystemExit("The Haskell bibliography source anchor changed.")

    next_alignment_id = max(int(row["alignment_id"].removeprefix("aln-")) for row in alignment if row["alignment_id"].startswith("aln-") and row["alignment_id"][4:].isdigit()) + 1
    planned_alignment = [dict(row) for row in alignment]
    primary_row = next(row for row in planned_alignment if row.get("candidate_id") == CID and not row.get("external_source"))
    primary_row["ku_id"] = KU_ID
    primary_row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}; identity source=BnF FRBNF12982918."
    planned_alignment.append({
        "alignment_id": f"aln-{next_alignment_id}",
        "candidate_id": CID,
        "ku_id": "",
        "external_source": "BnF Catalogue général",
        "external_id": BNF_URL,
        "decision": "new",
        "accessed_date": DATE,
        "process_ref": "S3-full-book-2026-10-16",
        "legacy_ku_id": "",
        "resolution_note": "Identity only: BnF person authority FRBNF12982918 identifies Gabriel-Jules de Cosnac (1819-1893), Comte and historian; it supplies exact birth/death dates and places and lists Jules de Cosnac as a rejected form. Supports the identity resolution, not all claims in Haskell or a formal author relation to the 1885 publication.",
    })
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "加布里埃尔-朱尔·德·科斯纳克",
        "name_en": "Gabriel-Jules de Cosnac",
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    planned_manifest.sort(key=lambda row: row["ku_id"])
    accepted_text = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))
    card = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    if not frontmatter_match or len(yaml.safe_load(frontmatter_match.group(1)).get("sources", [])) != 2:
        raise SystemExit("Generated person card frontmatter failed validation.")

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    detail = (
        f"### S4 person：Gabriel-Jules de Cosnac 人物组登记（{DATE}）\n\n"
        f"- `cand-7086`映射至 `units/persons/gabriel-jules-de-cosnac`。Haskell第21章书目列其为 *Les richesses du Palais Mazarin*（Paris, 1885）的责任者；BnF人物权威记录FRBNF12982918确认Gabriel-Jules de Cosnac（1819–1893）、伯爵、历史学家，并提供生卒年月日及地点。与该出版物的正式作者边留待S6。\n"
        f"- 新增1张person卡、1条manifest、1条候选KU映射、1条BnF身份行和accepted路径；S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person为{sync.fmt(stats['person']['registered_groups'])}组已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员待登记；KU总数{len(planned_manifest)}。字段事实由 `build_field_facts.py` 预检登记。\n\n"
    )
    if result_text.count("## 未解决项与交接限制") != 1:
        raise SystemExit("Could not locate result insertion point.")
    result_text = result_text.replace("## 未解决项与交接限制", detail + "## 未解决项与交接限制", 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    if f"### S4 person：Gabriel-Jules de Cosnac {GROUP}" in process_text:
        raise SystemExit("The S4 process record already exists.")
    process_text += (
        f"\n\n### S4 person：Gabriel-Jules de Cosnac {GROUP}（{DATE}）\n\n"
        f"- `{CID}`登记至`{KU_ID}`。Haskell书目p.420将Comte Gabriel-Jules de Cosnac列为 *Les richesses du Palais Mazarin*（Paris, 1885）的书内责任者形式；BnF人物权威FRBNF12982918支持其规范名、伯爵/历史学家称谓、生卒年月日及地点，异名含Jules de Cosnac。\n"
        "- 新增person卡、manifest、候选映射、accepted路径及BnF外部身份行。与1885刊本的正式作者关系、其书内引文与1661年清单的关系仍待S6；未将书目归属转成正式边。字段事实待运行`build_field_facts.py`。"
    )

    targets = [ALIGNMENT, MANIFEST, ACCEPTED, PROCESS, RESULT]
    backup_paths = [path.with_name(path.name + BACKUP_SUFFIX) for path in targets]
    if any(path.exists() for path in backup_paths):
        raise SystemExit("A de Cosnac S4 recovery copy already exists.")
    if args.dry_run:
        print(f"dry-run passed: {CID} -> {KU_ID}; external=aln-{next_alignment_id}; manifest={len(manifest)}->{len(planned_manifest)}")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}")
        return 0

    for original, backup in zip(targets, backup_paths, strict=True):
        shutil.copy2(original, backup)
    CARD_PATH.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(ALIGNMENT, alignment_fields, planned_alignment)
    sync.write_csv(MANIFEST, manifest_fields, planned_manifest)
    ACCEPTED.write_text(accepted_text, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: {CID} -> {KU_ID}; external=aln-{next_alignment_id}; manifest={len(planned_manifest)}")
    print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
