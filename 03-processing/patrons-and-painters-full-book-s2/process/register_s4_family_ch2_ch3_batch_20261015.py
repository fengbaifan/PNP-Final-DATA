from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
UNITS = ROOT / "04-knowledge" / "units"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-family-ch2-ch3"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def family(candidate, slug, zh, en, page, file, lines, quote, summary, desc_zh, desc_en, context_zh, context_en, scope_zh, scope_en):
    chapter = "2" if file.startswith("02_") else "3"
    return {
        "group": f"sg3-family-cand-{candidate.removeprefix('cand-')}",
        "candidates": [candidate],
        "slug": slug,
        "name_zh": zh,
        "name_en": en,
        "description_zh": desc_zh,
        "description_en": desc_en,
        "context_zh": context_zh,
        "context_en": context_en,
        "scope_zh": scope_zh,
        "scope_en": scope_en,
        "source": {
            "chapter": chapter,
            "page": page,
            "file": file,
            "lines": lines,
            "quote": quote,
            "summary": summary,
        },
    }


BATCH = [
    family("cand-4212", "orsini-family", "奥尔西尼家族", "Orsini family", "31", "02_CHP-2_sec_ii.md", "7–8", "the Orsini sold their estates at Monte Rotondo to Carlo Barberini", "哈斯克尔称奥尔西尼家族于1624年将蒙特罗通多的地产售予 Carlo Barberini。", "哈斯克尔称奥尔西尼家族于1624年将蒙特罗通多的地产售予 Carlo Barberini。本卡保留家族层级的集体交易陈述，不指定具体出售者。", "Haskell says the Orsini sold their estates at Monte Rotondo to Carlo Barberini in 1624. This card preserves the collective family-level sale and does not identify an individual seller.", "第2章以 Orsini 家族为集体主语记述1624年的地产出售。", "Chapter 2 uses the Orsini collectively in its account of the 1624 estate sale.", "不将地产出售归给某一位 Orsini 成员。", "Do not assign the estate sale to a particular Orsini member."),
    family("cand-4247", "house-of-este", "埃斯特家族（埃斯特王朝）", "House of Este", "25", "02_CHP-2_sec_i.md", "49–50", "art treasures accumulated by the Este over the centuries were looted", "哈斯克尔称 Ferrara 的 Este 家族数百年积累的艺术珍宝在教皇接管城市时遭到掠夺。", "哈斯克尔将埃斯特家族作为 Ferrara 历代积累艺术珍宝的集体主体。本卡不列举家族成员或逐件扩展珍宝清单。", "Haskell presents the House of Este as the collective family behind art treasures accumulated in Ferrara over centuries. This card does not enumerate members or expand the list of treasures.", "第2章将艺术珍宝的积累归于埃斯特家族，并记述 Ferrara 被接管后的掠夺。", "Chapter 2 attributes the accumulated art treasures to the Este and reports their looting after Ferrara was taken.", "此处是王朝／家族集体指称，不扩展为某一成员的收藏。", "This is a collective dynastic reference, not a collection attributed to an individual member."),
    family("cand-4348", "ludovisi-family", "卢多维西家族", "Ludovisi family", "30", "02_CHP-2_sec_i.md", "116–117", "Ludovisi monopolised Bernini’s output", "哈斯克尔称1621年后，卢多维西家族垄断了 Bernini 的创作。", "哈斯克尔以复数集体称谓记述1621年后卢多维西家族对 Bernini 创作的垄断。本卡不把这一说法归给某位家族成员。", "Haskell uses the collective Ludovisi to describe their monopolising Bernini’s output after 1621. This card does not assign the claim to an individual family member.", "第2章以家族集体指称描述1621年后的 Bernini 委托格局。", "Chapter 2 uses the family collectively in its account of Bernini’s commissions after 1621.", "保持来源中的复数家族指称，不指定个人赞助人。", "Preserve the source’s plural family reference without specifying an individual patron."),
    family("cand-4637", "sforza-family-valmontone", "斯福尔扎家族（瓦尔蒙托内语境）", "Sforza family (Valmontone account)", "47", "02_CHP-2_sec_iv.md", "51–52", "the palace of the Sforzas, a family which was compelled", "哈斯克尔称 Francesco Barberini 于1626年接收斯福尔扎家族的宫殿，数年后该家族被迫出售瓦尔蒙托内的财产。", "哈斯克尔在 Barberini 宫殿叙述中称斯福尔扎家族曾持有该宫殿，后来被迫出售瓦尔蒙托内财产。本卡与个人 Alessandro Sforza 及宫殿地点候选分别处理。", "In his account of the Barberini palace, Haskell says the Sforza family held the palace and later had to sell property at Valmontone. This family record remains distinct from Alessandro Sforza as a person and from the palace as a place.", "第2章把宫殿原有持有者表述为 Sforza 家族，并另提其瓦尔蒙托内财产。", "Chapter 2 identifies the former palace holders as the Sforza family and separately mentions their Valmontone property.", "不把家族指称并入个人 Alessandro Sforza 或地点候选。", "Do not merge the family reference with the person Alessandro Sforza or the place candidate."),
    family("cand-4646", "della-rovere-family", "德拉·罗韦雷家族", "Della Rovere family", "47", "02_CHP-2_sec_iv.md", "48–49", "a post which had belonged until their extinction to the Della Rovere", "哈斯克尔称罗马 Prefect 一职在德拉·罗韦雷家族灭绝前曾属于该家族，随后说明其乌尔比诺公爵身份。", "哈斯克尔将 Prefect of Rome 一职的历史归属追溯到德拉·罗韦雷家族，并称其家族在灭绝前拥有该职位。本卡不延伸为完整家谱。", "Haskell traces the former Prefect of Rome office to the Della Rovere family and says the family held it until its extinction. This card does not supply a full genealogy.", "第2章将该家族与罗马 Prefect 职位及乌尔比诺公爵身份相联系。", "Chapter 2 connects the family with the Prefect of Rome office and the dukes of Urbino.", "家族与个别 Della Rovere 统治者保持区分。", "Keep the family distinct from individual Della Rovere rulers."),
    family("cand-4651", "bentivoglio-family", "本蒂沃利奥家族", "Bentivoglio family", "48", "02_CHP-2_sec_iv.md", "57–58", "The Bentivoglio came from Ferrara, where they had for centuries been one of the most distinguished families", "哈斯克尔称本蒂沃利奥家族来自 Ferrara，数世纪来一直是当地最显赫的家族之一；其家族为 Taddeo Barberini 提供建议。", "哈斯克尔称本蒂沃利奥家族来自 Ferrara，并记述其家族长期显赫以及后来为 Taddeo Barberini 提供建议。本卡不把家族整体行为归给 Enzo、Guido 或 Ippolito 中的任何一人。", "Haskell says the Bentivoglio came from Ferrara and had long been one of its most distinguished families; he also describes the family as advising Taddeo Barberini. This card does not assign the family-level account to Enzo, Guido, or Ippolito individually.", "第2章以家族层级描述本蒂沃利奥的 Ferrara 出身、历史地位及其与 Barberini 宫廷的联系。", "Chapter 2 describes the Bentivoglio at family level: their Ferrara origin, standing, and connection with the Barberini court.", "不与分别识别的 Enzo、Guido、Ippolito 人物候选合并。", "Do not merge with the separately identified people Enzo, Guido, or Ippolito Bentivoglio."),
    family("cand-4659", "lante-family", "兰特家族", "Lante family", "49", "02_CHP-2_sec_iv.md", "77–77", "The Bentivoglio sold the palace to the Lante family", "哈斯克尔称本蒂沃利奥家族将宫殿售予兰特家族，之后 Cardinal Mazarin 从兰特家族取得该宫殿。", "哈斯克尔在宫殿转手叙述中将兰特家族列为本蒂沃利奥之后、Mazarin 之前的持有方。本卡不把后续取得者 Mazarin 并入家族。", "In the palace transfer account, Haskell places the Lante family between the Bentivoglio and Cardinal Mazarin as successive holders. This record does not merge Mazarin into the family.", "第2章脚注指出本蒂沃利奥将宫殿售予兰特家族，Mazarin 后来从兰特家族取得。", "Chapter 2’s note says the Bentivoglio sold the palace to the Lante, from whom Mazarin later acquired it.", "与后续个人取得者 Cardinal Mazarin 区分。", "Keep distinct from the later individual acquirer, Cardinal Mazarin."),
    family("cand-4874", "altemps-family", "阿尔滕普斯家族", "Altemps family", "58", "02_CHP-2_sec_iv.md", "214–214", "The palace was bought by Bentivoglio from the Altemps family in 1619", "哈斯克尔称 Bentivoglio 于1619年从阿尔滕普斯家族购得该宫殿。", "哈斯克尔把阿尔滕普斯家族列为 Bentivoglio 于1619年购置宫殿时的前持有家族。本卡不识别具体出售者。", "Haskell names the Altemps family as the former holders from whom Bentivoglio bought the palace in 1619. This card does not identify an individual seller.", "第2章脚注记载 Bentivoglio 于1619年从阿尔滕普斯家族购得宫殿。", "A chapter-two note reports Bentivoglio’s 1619 purchase of the palace from the Altemps family.", "来源未命名具体出售者或家族支系。", "The source names neither an individual seller nor a family branch."),
    family("cand-5006", "farnese-family", "法尔内塞家族", "Farnese family", "66", "03_CHP-3_sec_ii.md", "8–9", "Farnese had specifically reserved the adornment of the tribune", "哈斯克尔称 Farnese 为其家族专门保留了耶稣教堂祭坛区与主祭坛的装饰权，其继承人因此掌握后续工程的许可。", "哈斯克尔称 Farnese 为其家族保留耶稣教堂祭坛区及主祭坛的装饰权。本卡只记录家族层级的保留安排，与 Cardinal Alessandro Farnese 个人分开。", "Haskell says Farnese reserved decoration of the Gesù tribune and High Altar for his family. This record captures the family-level reservation and remains distinct from Cardinal Alessandro Farnese as an individual.", "第3章称 Farnese 家族保留了耶稣教堂祭坛区和主祭坛的装饰权。", "Chapter 3 says the Farnese reserved the Gesù tribune and High Altar decoration for their family.", "不把家族身份与 Cardinal Alessandro Farnese 个人身份混为一项。", "Keep the family identity separate from Cardinal Alessandro Farnese as a person."),
    family("cand-5011", "caetani-family", "卡埃塔尼家族", "Caetani family", "66", "03_CHP-3_sec_ii.md", "10–11", "older aristocratic families of Rome, such as the Orsini, the Caetani", "哈斯克尔将卡埃塔尼列为罗马较早的贵族家族之一，并把家族女性与耶稣会教堂侧礼拜堂的赞助背景联系起来。", "哈斯克尔将卡埃塔尼列为罗马较早的贵族家族之一。本卡限于这一家族类别和礼拜堂语境，不推断支系或具体女性成员。", "Haskell lists the Caetani among Rome’s older aristocratic families in a passage about women’s connection with the Gesù side chapels. This card does not infer a branch or identify particular female members.", "第3章以卡埃塔尼为罗马旧贵族家族的例子，讨论其与耶稣会教堂侧礼拜堂的关系。", "Chapter 3 uses the Caetani as an example of Rome’s older aristocratic families in its discussion of the Gesù side chapels.", "来源没有指定家族支系或具体成员。", "The source specifies neither a family branch nor individual members."),
    family("cand-5012", "mellini-family-rome", "梅利尼家族", "Mellini family", "66", "03_CHP-3_sec_ii.md", "10–11", "the Meliini", "哈斯克尔将 OCR 所写 Meliini 列为罗马较早的贵族家族之一；S3 候选记录说明印刷扫描读作 Mellini。", "哈斯克尔将此家族列为罗马较早的贵族家族之一。OCR 正文读作 Meliini，S3 候选记录的印刷扫描读法为 Mellini；不据此推断具体支系。", "Haskell lists this among Rome’s older aristocratic families. The OCR reads Meliini, while the S3 candidate note records Mellini as the print-scan reading; no branch is inferred.", "第3章的家族名录位于耶稣会教堂侧礼拜堂的讨论中。", "The family list appears in Chapter 3’s discussion of the Gesù side chapels.", "保留 OCR 与印刷扫描读法差异，不作支系识别。", "Preserve the OCR and print-scan readings without identifying a branch."),
    family("cand-5030", "cesi-family", "切西家族", "Cesi family", "69", "03_CHP-3_sec_ii.md", "43–44", "he and his family were to enjoy overriding privileges", "哈斯克尔称 Cardinal Pier Donato Cesi 与其家族在新教堂会务中取得优先特权，后来其兄 Angelo Cesi 延续了家族赞助。", "哈斯克尔称 Pier Donato Cesi 及其家族取得新教堂会务中的优先权，并说 Angelo Cesi 后来延续家族赞助。本卡保持家族与两位个人的层级区分。", "Haskell says Pier Donato Cesi and his family received overriding privileges in the congregation’s affairs, and that Angelo Cesi later continued the family patronage. This card keeps the family distinct from both people.", "第3章将家族特权和赞助延续分别关联于 Pier Donato 与 Angelo Cesi。", "Chapter 3 links the family’s privileges and continued patronage with Pier Donato and Angelo Cesi respectively.", "不与 Cardinal Pier Donato Cesi 或 Angelo Cesi 人物候选合并。", "Do not merge with the person candidates Cardinal Pier Donato Cesi or Angelo Cesi."),
    family("cand-5113", "mignanelli-family", "米尼亚内利家族", "Mignanelli family", "75", "03_CHP-3_sec_ii.md", "131–132", "Bernardino acquired from the Mignanelli in 1632", "哈斯克尔称 Bernardino 于1632年从米尼亚内利家族购得一座十六世纪宫殿，之后在其中汇集绘画收藏。", "哈斯克尔称 Bernardino 于1632年从米尼亚内利家族购得宫殿。本卡只记录家族作为书中集体前持有方，不补写具体出售者或完整产权史。", "Haskell says Bernardino acquired a sixteenth-century palace from the Mignanelli in 1632. This card records the family as the collective former holders and does not supply an individual seller or full title history.", "第3章以 Mignanelli 家族为宫殿先前持有方，并另述 Bernardino 在宫中集画。", "Chapter 3 names the Mignanelli as prior holders of the palace and separately describes Bernardino’s picture collection there.", "不据此推定具体出售者或完整产权链。", "Do not infer an individual seller or a complete chain of title."),
    family("cand-5179", "medici-family", "美第奇家族", "Medici family", "76", "03_CHP-3_sec_iv.md", "6–6", "many promises to continue working for the Medici", "哈斯克尔称 Pietro da Cortona 在 Palazzo Pitti 工作，并承诺继续为美第奇家族效力。", "哈斯克尔将美第奇作为 Pietro da Cortona 承诺继续效力的家族赞助主体。本卡保留集体王朝身份，不列家族成员或逐项作品。", "Haskell names the Medici as the family patron for whom Pietro da Cortona promised to continue working while engaged at Palazzo Pitti. This record preserves the collective dynastic reference without listing members or works.", "第3章将 Medici 作为 Pietro da Cortona 的家族赞助主体。", "Chapter 3 refers to the Medici collectively as patrons for whom Pietro da Cortona promised continued work.", "不指定具体 Medici 成员。", "No particular Medici member is specified."),
    family("cand-5417", "savelli-family", "萨韦利家族", "Savelli family", "92", "03_CHP-3_sec_iv.md", "165–167", "The site officially still belonged to the Savelli", "哈斯克尔称 St Ignatius 礼拜堂所在地名义上仍属萨韦利家族，Prince Giulio 作为家族首领放弃了该家族对礼拜堂的赞助权。", "哈斯克尔将 St Ignatius 礼拜堂所在地及原有赞助权归于萨韦利家族，并称 Prince Giulio 以家族首领身份放弃该权利。本卡不确定精确产权名称或家族结构。", "Haskell says the St Ignatius chapel site officially still belonged to the Savelli and that Prince Giulio, as family head, gave up the family patronage. This card does not resolve the exact property title or family structure.", "第3章将场地、礼拜堂赞助权与 Prince Giulio 的家族首领身份相连。", "Chapter 3 links the site, chapel patronage, and Prince Giulio’s role as family head.", "精确产权名称及完整家族结构仍未核定。", "The exact property title and full family structure remain unresolved."),
]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note: str) -> str | None:
    match = re.search(r"group=([^;]+)", note)
    return match.group(1) if match else None


def make_card(record: dict) -> str:
    source = record["source"]
    span = f"lines {source['lines']}; print p. {source['page']}"
    frontmatter = {
        "title": f"{record['name_zh']}（{record['name_en']}）",
        "name_en": record["name_en"],
        "type": "family",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": f"{BOOK_CITATION}, ch. {source['chapter']}, p. {source['page']}.",
                "location": f"第{source['chapter']}章，印刷页{source['page']}；OCR L{source['lines']}",
                "sentence_summary": source["summary"],
                "original_quotes": [{"source_span": f"lines {source['lines']}", "text": source["quote"]}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": f"02-sources/02-Markdown/{source['file']}",
                    "source_span": span,
                },
            }
        ],
        "created": "2026-10-15",
        "updated": "2026-10-15",
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** {record['description_zh']}

**English:** {record['description_en']}

### 名称

中文名为{record['name_zh']}；英文名为 {record['name_en']}。原书中的家族名称为 {record['name_en'].removesuffix(' family')}。

### 本书语境

{record['context_zh']}

{record['context_en']}

### 身份边界

中文：{record['scope_zh']}

English: {record['scope_en']}

## 关系与证据

本轮完成身份登记；正文中的家族成员、收藏与赞助陈述仍须按各自来源和端点在 S6 审查。本卡未新增正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="S4 registration for source-backed ch. 2–3 family groups")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.apply:
        parser.error("choose exactly one of --dry-run or --apply")

    manifest_path = TABLES / "ku-manifest.csv"
    alignment_path = TABLES / "alignment.csv"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    candidate_path = TABLES / "entity-candidates.csv"
    manifest_fields, manifest = read_csv(manifest_path)
    alignment_fields, alignments = read_csv(alignment_path)
    _, candidates = read_csv(candidate_path)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    alignment_by_id = {
        r["candidate_id"]: r for r in alignments
        if r.get("candidate_id") and not r.get("external_source")
    }
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")
    manifest_by_id = {r["ku_id"]: r for r in manifest}

    assert len(manifest) == 1067, f"unexpected manifest count: {len(manifest)}"
    new_rows = [r for r in alignments if not r.get("external_source") and r.get("decision") == "new"]
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    registered: dict[str, list[dict[str, str]]] = defaultdict(list)
    family_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
        if row.get("ku_id"):
            registered[group].append(row)
        if candidate_by_id[row["candidate_id"]].get("suggested_type") == "family":
            family_groups[group].append(row)
    assert len(new_rows) == 5007 and len(groups) == 4830
    assert len(registered) == 48 and sum(map(len, registered.values())) == 53
    assert len(family_groups) == 80 and sum(map(len, family_groups.values())) == 85

    candidates_in_batch = [cid for record in BATCH for cid in record["candidates"]]
    assert len(BATCH) == 15 and len(candidates_in_batch) == len(set(candidates_in_batch)) == 15
    for record in BATCH:
        assert len(record["candidates"]) == 1
        candidate_id = record["candidates"][0]
        candidate = candidate_by_id[candidate_id]
        alignment = alignment_by_id[candidate_id]
        assert candidate.get("suggested_type") == "family"
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert get_group(alignment["resolution_note"]) == record["group"]
        path = UNITS / "families" / f"{record['slug']}.md"
        rel_path = f"04-knowledge/units/families/{record['slug']}.md"
        ku_id = f"units/families/{record['slug']}"
        assert not path.exists(), f"refusing to overwrite {path}"
        assert not any(r["ku_id"] == ku_id or r["card_path"] == rel_path for r in manifest)
        assert rel_path not in accepted_text
        source = record["source"]
        source_path = ROOT / "02-sources" / "02-Markdown" / source["file"]
        assert source["quote"] in source_path.read_text(encoding="utf-8-sig"), (
            record["slug"], source["quote"]
        )

    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {
        r["candidate_id"]: r for r in planned_alignments
        if r.get("candidate_id") and not r.get("external_source")
    }
    for record in BATCH:
        candidate_id = record["candidates"][0]
        ku_id = f"units/families/{record['slug']}"
        row = planned_by_id[candidate_id]
        row["ku_id"] = ku_id
        row["resolution_note"] += f" S4 registration: mapped {record['group']} to {ku_id}."

    planned_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in planned_alignments:
        if row.get("external_source") or row.get("decision") != "new":
            continue
        planned_groups[get_group(row["resolution_note"])].append(row)
    planned_registered = {
        g: rows for g, rows in planned_groups.items() if any(r.get("ku_id") for r in rows)
    }
    for group, rows in planned_registered.items():
        mapped = [r for r in rows if r.get("ku_id")]
        assert len(mapped) == len(rows) and len({r["ku_id"] for r in rows}) == 1, group
    assert len(planned_registered) == 63
    assert sum(len(rows) for rows in planned_registered.values()) == 68

    if args.dry_run:
        print(
            f"dry-run passed: groups={len(BATCH)} candidates={len(candidates_in_batch)} "
            f"new_groups={len(planned_groups)} registered_groups={len(planned_registered)} "
            f"registered_candidates={sum(len(rows) for rows in planned_registered.values())} "
            f"manifest_after={len(manifest) + len(BATCH)}"
        )
        return 0

    for record in BATCH:
        path = UNITS / "families" / f"{record['slug']}.md"
        path.write_text(make_card(record), encoding="utf-8-sig", newline="\n")
        manifest.append(
            {
                "ku_id": f"units/families/{record['slug']}",
                "type": "family",
                "canonical_name": record["name_zh"],
                "name_en": record["name_en"],
                "source_task": TASK,
                "card_path": f"04-knowledge/units/families/{record['slug']}.md",
            }
        )
    write_csv(manifest_path, manifest_fields, manifest)
    write_csv(alignment_path, alignment_fields, planned_alignments)
    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/institutions/")),
        len(accepted_lines),
    )
    accepted_lines[insert_at:insert_at] = [
        f"- 04-knowledge/units/families/{record['slug']}.md" for record in BATCH
    ]
    accepted_path.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    print(f"applied {len(BATCH)} family groups and {len(candidates_in_batch)} candidate mappings; manifest={len(manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
