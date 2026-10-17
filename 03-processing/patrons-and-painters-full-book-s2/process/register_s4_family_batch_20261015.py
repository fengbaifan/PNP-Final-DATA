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
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-family-reviewed"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


REGIONS = {
    "Genoa": {
        "zh": "哈斯克尔将 {name} 列入热那亚富裕商业贵族的主要家族，并称这些家族以本地画家作品、从博洛尼亚带回的当代绘画和古代大师作品充实宫殿。此条保留书中的集体家族身份，不据此推定具体成员或支系。",
        "en": "Haskell lists the {name} among the principal families of Genoa’s wealthy mercantile aristocracy and says these families filled their palaces with works by local painters, occasional contemporary pictures from Bologna, and old masters. This record preserves the collective family reference without inferring particular members or branches.",
        "summary": "本章将 {name} 列入热那亚主要商业贵族家族名录，并把这些家族的宫殿收藏概括为本地画家、博洛尼亚当代作品及古代大师作品。",
        "summary_en": "The chapter lists the {name} among Genoa’s principal mercantile families and describes the group’s palace holdings as works by local painters, contemporary pictures from Bologna, and old masters.",
        "context_zh": "第8章第203页将其列入热那亚主要商业贵族家族，并以集体语法描述这些家族的宫殿收藏。",
        "context_en": "Chapter 8, page 203, lists it among Genoa’s principal mercantile families and describes the group’s palace collections collectively.",
        "pages": "203",
    },
    "Naples": {
        "zh": "哈斯克尔将 {name} 列入那不勒斯的封建土地家族，并称这组家族在西班牙统治下兴盛，慷慨支持当地画派。此条仅保留书中的集体指称，不补写支系或成员。",
        "en": "Haskell lists the {name} among Naples’s feudal landowning families and says this group prospered under Spanish rule and generously supported the local school of art. This record preserves the collective family reference without supplying branches or members.",
        "summary": "本章将 {name} 列入那不勒斯封建土地家族，并称这些家族在西班牙统治下兴盛、支持当地画派。",
        "summary_en": "The chapter lists the {name} among Naples’s feudal landowning families and says the group prospered under Spanish rule and supported the local school of art.",
        "context_zh": "第8章第203页将其列入那不勒斯封建土地家族；关于兴盛与赞助的描述针对该组家族。",
        "context_en": "Chapter 8, page 203, lists it among Naples’s feudal landowners; the statement about prosperity and patronage refers to the group collectively.",
        "pages": "203",
    },
    "Bologna": {
        "zh": "哈斯克尔将 {name} 列入博洛尼亚的元老家族；本段称这些家族统治城市、保留部分自治，并建立大型艺术收藏。此条不补入支系、成员或作品清单。",
        "en": "Haskell lists the {name} among Bologna’s senatorial families; the passage says these families ruled the city, retained some semblance of autonomy, and built extensive art collections. This record does not add branches, members, or an itemized collection.",
        "summary": "本章将 {name} 列入博洛尼亚元老家族，并称这些家族统治城市、保留部分自治及建立大型艺术收藏。",
        "summary_en": "The chapter lists the {name} among Bologna’s senatorial families and says these families ruled the city, retained some autonomy, and built extensive art collections.",
        "context_zh": "第8章第203页将其列入博洛尼亚元老家族；自治与收藏的说明针对该组家族。",
        "context_en": "Chapter 8, page 203, lists it among Bologna’s senatorial families; the statements about autonomy and collections apply to the group collectively.",
        "pages": "203",
    },
}


def city_family(
    candidate: str,
    slug: str,
    name_zh: str,
    name_en: str,
    surname: str,
    region: str,
    quote: str,
    source_lines: str,
    *,
    extra_zh: str = "",
    extra_en: str = "",
) -> dict:
    data = REGIONS[region]
    base_zh = data["zh"].format(name=surname)
    base_en = data["en"].format(name=name_en)
    if extra_zh:
        base_zh += " " + extra_zh
    if extra_en:
        base_en += " " + extra_en
    return {
        "group": f"sg3-family-cand-{candidate.removeprefix('cand-')}",
        "candidates": [candidate],
        "slug": slug,
        "name_zh": name_zh,
        "name_en": name_en,
        "description_zh": base_zh,
        "description_en": base_en,
        "context_zh": data["context_zh"].format(name=surname),
        "context_en": data["context_en"].format(name=name_en),
        "source": {
            "chapter": "8",
            "pages": data["pages"],
            "file": "08_CHP-8_sec_i.md",
            "lines": source_lines,
            "summary": data["summary"].format(name=surname),
            "quote": quote,
        },
    }


FAMILY_GROUPS = [
    {
        "group": "sg3-family-chigi",
        "candidates": ["cand-6329", "cand-6484"],
        "slug": "chigi-family-alexander-vii",
        "name_zh": "基吉家族",
        "name_en": "Chigi family",
        "description_zh": "哈斯克尔在亚历山大七世亲属的叙述中将马里奥及其子侄置于基吉家族语境，并称家族势力日益增长；在克勉十世时期的比较中，他又以“a Chigi”说明奢侈规模。此条保留集体家族身份，不将比较语句归给某个成员。",
        "description_en": "In his account of Alexander VII’s relatives, Haskell places Mario and his nephews in the Chigi family context and describes the family as growing in wealth and influence; in the Clement X passage he uses “a Chigi” as a comparison for the scale of luxury. This record preserves the collective family identity and does not assign the comparison to an individual member.",
        "context_zh": "cand-6329 的第6章第154页来源与 cand-6484 的第162页跨页比较共同指向基吉家族；两者没有给出不同支系。",
        "context_en": "The chapter-six source for cand-6329 on page 154 and the continuation for cand-6484 on page 162 both refer to the Chigi family; neither distinguishes a separate branch.",
        "sources": [
            {
                "chapter": "6",
                "pages": "154",
                "file": "06_CHP-6_sec_i.md",
                "lines": "96–96",
                "summary": "哈斯克尔在亚历山大七世亲属语境中称基吉家族日益富有和强势，并提及马里奥及其子侄。",
                "quote": "the family grew ever richer and more overbearing",
            },
            {
                "chapter": "6",
                "pages": "161–162",
                "file": "06_CHP-6_sec_v.md",
                "lines": "11–15",
                "summary": "第161页对 Barberini 的比较在跨页处续接，第162页以 a Chigi 作同一奢侈规模比较。",
                "quote": "or a Chigi",
            },
        ],
    },
    {
        "group": "sg3-family-del-rosso-florence",
        "candidates": ["cand-7489", "cand-8078"],
        "slug": "del-rosso-family-florence",
        "name_zh": "佛罗伦萨德尔·罗索家族",
        "name_en": "Del Rosso family of Florence",
        "description_zh": "哈斯克尔将德尔·罗索描述为富有的佛罗伦萨商人家族，列出 Andrea、Lorenzo、Ottavio 及兄弟 Nicola；另称 1706 年佛罗伦萨展览中的那不勒斯作品主要由 del Rosso 兄弟借出。此条将两处集体指称合为同一书内家族身份，不推定各幅作品由哪位兄弟出借。",
        "description_en": "Haskell describes the Del Rosso as a wealthy Florentine merchant family and names Andrea, Lorenzo, Ottavio, and their brother Nicola; he later says the del Rosso brothers lent most of the Neapolitan contingent at the 1706 Florentine exhibition. These collective references are grouped as one family identity in the book, without assigning individual loans to a particular brother.",
        "context_zh": "第8章第211页列出 Del Rosso 家族及兄弟，第241页在佛罗伦萨展览语境中再次称 del Rosso brothers；书中没有提示另一个同名家族或不同支系。",
        "context_en": "Chapter 8, page 211, identifies the Del Rosso family and brothers; page 241 again refers to the del Rosso brothers in the context of a Florentine exhibition. The book does not indicate a separate family or branch.",
        "sources": [
            {
                "chapter": "8",
                "pages": "211",
                "file": "08_CHP-8_sec_i.md",
                "lines": "85–86",
                "summary": "哈斯克尔称这些兄弟来自一个富有的商人家族，并在此处交代家族身份与其在佛罗伦萨的社会上升。",
                "quote": "They sprang from a family of rich merchants",
            },
            {
                "chapter": "8",
                "pages": "241",
                "file": "08_CHP-8_sec_ii.md",
                "lines": "366–366",
                "summary": "哈斯克尔称 1706 年展览中的那不勒斯作品主要由 del Rosso 兄弟借出；未逐件指定出借人。",
                "quote": "mainly lent by the del Rosso brothers",
            },
        ],
    },
    city_family(
        "cand-7357", "genoa-balbi-family", "巴尔比家族", "Balbi family", "Balbi",
        "Genoa", "the Balbi and the Brignole", "5–6",
        extra_zh="本项与书中后文单独提及的 Paolo Battista Balbi 个人候选区分。",
        extra_en="This family record remains distinct from the separately named individual Paolo Battista Balbi later in the chapter.",
    ),
    city_family("cand-7358", "genoa-brignole-family", "布里尼奥莱家族", "Brignole family", "Brignole", "Genoa", "the Balbi and the Brignole", "5–6"),
    city_family("cand-7359", "genoa-doria-family", "多利亚家族", "Doria family", "Doria", "Genoa", "the Doria and Durazzo", "5"),
    city_family("cand-7360", "genoa-durazzo-family", "杜拉佐家族", "Durazzo family", "Durazzo", "Genoa", "the Doria and Durazzo", "5–6"),
    city_family(
        "cand-7361", "genoa-imperiali-family", "因佩里亚利家族", "Imperiali family", "Imperiali",
        "Genoa", "the Imperial!", "5",
        extra_zh="S3 候选记录指出印刷扫描读作 Imperiali，而 OCR 正文作 Imperial!；此条保留异读，不识别具体支系。",
        extra_en="The S3 candidate note records the print scan as Imperiali while the OCR text reads Imperial!; this card preserves the variant and identifies no branch.",
    ),
    city_family("cand-7362", "genoa-lomellini-family", "洛梅利尼家族", "Lomellini family", "Lomellini", "Genoa", "Lomellini and Negroni", "5–6"),
    city_family(
        "cand-7363", "genoa-negroni-family", "内格罗尼家族", "Negroni family", "Negroni", "Genoa", "Lomellini and Negroni", "5–6",
        extra_zh="此集体家族项与单独索引的 Cardinal Negroni 人物候选区分。",
        extra_en="This collective family record remains distinct from the separately indexed person Cardinal Negroni.",
    ),
    city_family("cand-7364", "genoa-pallavicini-family", "帕拉维奇尼家族", "Pallavicini family", "Pallavicini", "Genoa", "the Pallavicini, Saluzzi, Sauli and Spinola", "6"),
    city_family("cand-7365", "genoa-saluzzi-family", "萨卢齐家族", "Saluzzi family", "Saluzzi", "Genoa", "the Pallavicini, Saluzzi, Sauli and Spinola", "6"),
    city_family("cand-7366", "genoa-sauli-family", "萨乌利家族", "Sauli family", "Sauli", "Genoa", "the Pallavicini, Saluzzi, Sauli and Spinola", "6"),
    city_family("cand-7367", "genoa-spinola-family", "斯皮诺拉家族", "Spinola family", "Spinola", "Genoa", "the Pallavicini, Saluzzi, Sauli and Spinola", "6"),
    city_family("cand-7369", "naples-maddaloni-family", "马达洛尼家族", "Maddaloni family", "Maddaloni", "Naples", "the Colonnas and the Maddalonis", "6–7"),
    city_family("cand-7370", "naples-monteleone-family", "蒙特莱奥内家族", "Monteleone family", "Monteleone", "Naples", "the Monteleones", "7"),
    city_family("cand-7371", "naples-sonnino-family", "索尼诺家族", "Sonnino family", "Sonnino", "Naples", "the Sonninos", "7"),
    city_family(
        "cand-7372", "naples-tarsia-spinelli-family", "塔尔西亚·斯皮内利家族", "Tarsia Spinelli family", "Tarsia Spinelli",
        "Naples", "the Tarsia\nSpinellis", "7–8",
        extra_zh="OCR 将复数形式拆在跨行位置；本项沿候选裁决保留为一个姓氏组合，不推定支系。",
        extra_en="The OCR breaks the plural form across a line; this record preserves the compound family name used in the candidate decision without inferring a branch.",
    ),
    city_family("cand-7373", "bologna-albergati-family", "阿尔贝加蒂家族", "Albergati family", "Albergati", "Bologna", "the Albergati and the Aldrovandi", "8"),
    city_family("cand-7374", "bologna-aldrovandi-family", "阿尔德罗万迪家族", "Aldrovandi family", "Aldrovandi", "Bologna", "the Albergati and the Aldrovandi", "8"),
    city_family("cand-7375", "bologna-ercolani-family", "埃尔科拉尼家族", "Ercolani family", "Ercolani", "Bologna", "the Ercolani and Ghisilieri", "8"),
    city_family("cand-7376", "bologna-ghisilieri-family", "吉西列里家族", "Ghisilieri family", "Ghisilieri", "Bologna", "the Ercolani and Ghisilieri", "8"),
    city_family("cand-7377", "bologna-pepoli-family", "佩波利家族", "Pepoli family", "Pepoli", "Bologna", "Pepoli and Sampieri", "8"),
    city_family("cand-7378", "bologna-sampieri-family", "桑皮耶里家族", "Sampieri family", "Sampieri", "Bologna", "Pepoli and Sampieri", "8"),
]


CROSSWALK = {
    "cand-4729": {
        "decision": "same",
        "ku_id": "units/families/borghese-family",
        "group": "sg3-ku-units-families-borghese-family",
        "note": "S3 cross-chapter review: the collective ‘the Borghese’ in the ch. 2 patronage comparison is the same family identity already represented by the accepted Borghese family KU; the source names no distinct branch or individual. Reuse that KU.",
    },
    "cand-4742": {
        "decision": "same",
        "ku_id": "units/families/aldobrandini-family",
        "group": "sg3-ku-units-families-aldobrandini-family",
        "note": "S3 cross-chapter review: the collective ‘the Aldobrandini’ in the ch. 2 Ferrara comparison is the same family identity already represented by the accepted Aldobrandini family KU; the source names no distinct branch or individual. Reuse that KU.",
    },
    "cand-6473": {
        "decision": "new",
        "ku_id": "units/families/barberini-family",
        "group": "sg3-family-barberini",
        "note": "S3/S4 cross-chapter review: the Barberini used as the scale comparator on pp. 161–162 are the same collective family as cand-0198 and cand-3464; the page-break continuation adds Chigi as a second comparator. Keep distinct from the Barberini household institution.",
    },
    "cand-6329": {
        "decision": "new",
        "ku_id": "units/families/chigi-family-alexander-vii",
        "group": "sg3-family-chigi",
        "note": "S3/S4 cross-chapter review: this family reference through Alexander VII’s relatives is grouped with cand-6484, where ‘a Chigi’ appears as a family-level comparator. The source does not distinguish branches.",
    },
    "cand-6484": {
        "decision": "new",
        "ku_id": "units/families/chigi-family-alexander-vii",
        "group": "sg3-family-chigi",
        "note": "S3/S4 cross-chapter review: the page-162 continuation ‘or a Chigi’ is grouped with cand-6329’s Chigi family reference through Alexander VII’s relatives. The source does not distinguish branches.",
    },
    "cand-7489": {
        "decision": "new",
        "ku_id": "units/families/del-rosso-family-florence",
        "group": "sg3-family-del-rosso-florence",
        "note": "S3/S4 cross-chapter review: group with cand-8078. The book identifies Andrea, Lorenzo, Ottavio, and Nicola del Rosso as brothers from the Florentine merchant family on p. 211, then refers to the del Rosso brothers in the 1706 Florentine exhibition on p. 241; no separate family or branch is indicated.",
    },
    "cand-8078": {
        "decision": "new",
        "ku_id": "units/families/del-rosso-family-florence",
        "group": "sg3-family-del-rosso-florence",
        "note": "S3/S4 cross-chapter review: group with cand-7489. The p. 241 reference to del Rosso brothers concerns the Florentine 1706 exhibition; p. 211 identifies the same book-context family and brothers. Preserve the collective lending claim without assigning individual loans.",
    },
    "cand-7368": {
        "decision": "undecided",
        "ku_id": "",
        "group": "sg3-review-colonna-family-branch",
        "note": "S3 cross-chapter review: Haskell names the Colonnas among Naples’s feudal landowning families on p. 203, but the book does not identify a branch or connect this reference to the existing Colonna family KU. Keep identity undecided; require source-specific or authoritative evidence establishing family scope before reuse or separate registration. Do not resolve by surname alone.",
    },
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def alignment_group(note: str) -> str | None:
    match = re.search(r"group=([^;]+)", note)
    return match.group(1) if match else None


def set_group(note: str, group: str) -> str:
    if re.search(r"group=[^;]+", note):
        return re.sub(r"group=[^;]+", f"group={group}", note, count=1)
    return f"group={group}; {note}"


def build_source(record: dict, source: dict) -> dict:
    lines = source["lines"]
    span = f"lines {lines}; print p. {source['pages']}"
    return {
        "citation": f"{BOOK_CITATION}, ch. {source['chapter']}, p. {source['pages']}.",
        "location": f"第{source['chapter']}章，印刷页{source['pages']}；OCR L{lines}",
        "sentence_summary": source["summary"],
        "original_quotes": [
            {"source_span": f"lines {lines}", "text": source["quote"]}
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/02-Markdown/{source['file']}",
            "source_span": span,
        },
    }


def make_card(record: dict) -> str:
    sources = record.get("sources")
    if sources is None:
        sources = [build_source(record, record["source"])]
    else:
        sources = [build_source(record, source) for source in sources]
    frontmatter = {
        "title": f"{record['name_zh']}（{record['name_en']}）",
        "name_en": record["name_en"],
        "type": "family",
        "evidence_status": "source_backed",
        "sources": sources,
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

中文名为{record['name_zh']}；英文名为 {record['name_en']}。原书使用的姓氏形式为 {record.get('surname', record['name_en'].removesuffix(' family'))}。

### 本书语境

{record['context_zh']}

{record['context_en']}

## 关系与证据

本轮完成身份登记；正文中的家族成员、收藏与赞助陈述仍须按各自来源和端点在 S6 审查。本卡未新增正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="S4 family identity crosswalk and registration batch")
    parser.add_argument("--dry-run", action="store_true", help="validate the planned crosswalk and registrations")
    parser.add_argument("--apply", action="store_true", help="write the reviewed family batch")
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
        r["candidate_id"]: r
        for r in alignments
        if r.get("candidate_id") and not r.get("external_source")
    }
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")
    manifest_by_id = {r["ku_id"]: r for r in manifest}

    assert len(manifest) == 1044, f"unexpected current manifest count: {len(manifest)}"
    current_family_new = [
        r for r in alignments
        if not r.get("external_source")
        and r.get("decision") == "new"
        and candidate_by_id.get(r["candidate_id"], {}).get("suggested_type") == "family"
    ]
    current_family_groups = {alignment_group(r["resolution_note"]) for r in current_family_new}
    assert len(current_family_new) == 88 and len(current_family_groups) == 86, (
        len(current_family_new), len(current_family_groups)
    )
    assert "units/families/barberini-family" in manifest_by_id
    assert (UNITS / "families" / "barberini-family.md").is_file()

    assert len(FAMILY_GROUPS) == 23
    target_candidate_ids = [cid for record in FAMILY_GROUPS for cid in record["candidates"]]
    assert len(target_candidate_ids) == len(set(target_candidate_ids)) == 25

    for candidate_id, update in CROSSWALK.items():
        row = alignment_by_id.get(candidate_id)
        assert row is not None, f"missing alignment row: {candidate_id}"
        assert row["decision"] == "new", (candidate_id, row["decision"])
        if candidate_id in {"cand-4729", "cand-4742", "cand-6473", "cand-6329", "cand-6484", "cand-7368", "cand-7489", "cand-8078"}:
            assert not row.get("ku_id"), f"unexpected pre-existing KU mapping: {candidate_id}"
    for record in FAMILY_GROUPS:
        path = UNITS / "families" / f"{record['slug']}.md"
        rel_path = f"04-knowledge/units/families/{record['slug']}.md"
        ku_id = f"units/families/{record['slug']}"
        assert not path.exists(), f"refusing to overwrite {path}"
        assert not any(r["ku_id"] == ku_id or r["card_path"] == rel_path for r in manifest)
        assert rel_path not in accepted_text
        for candidate_id in record["candidates"]:
            row = alignment_by_id[candidate_id]
            assert row["decision"] == "new", (candidate_id, row["decision"])
            assert candidate_by_id[candidate_id]["suggested_type"] == "family"
        source_list = record.get("sources") or [record["source"]]
        for source in source_list:
            source_path = ROOT / "02-sources" / "02-Markdown" / source["file"]
            text = source_path.read_text(encoding="utf-8-sig")
            assert source["quote"] in text, f"quote not found for {record['slug']}: {source['quote']!r}"

    planned_alignments = [dict(r) for r in alignments]
    planned_by_id = {
        r["candidate_id"]: r
        for r in planned_alignments
        if r.get("candidate_id") and not r.get("external_source")
    }
    for candidate_id, update in CROSSWALK.items():
        row = planned_by_id[candidate_id]
        row["decision"] = update["decision"]
        row["ku_id"] = update["ku_id"]
        row["resolution_note"] = set_group(row["resolution_note"], update["group"])
        row["resolution_note"] += f" S3/S4 cross-chapter decision: {update['note']}"
    for record in FAMILY_GROUPS:
        ku_id = f"units/families/{record['slug']}"
        for candidate_id in record["candidates"]:
            row = planned_by_id[candidate_id]
            row["ku_id"] = ku_id
            row["resolution_note"] = set_group(row["resolution_note"], record["group"])
            row["resolution_note"] += f" S4 registration: mapped to {ku_id}."

    planned_new = [r for r in planned_alignments if not r.get("external_source") and r["decision"] == "new"]
    planned_same = [r for r in planned_alignments if not r.get("external_source") and r["decision"] == "same"]
    planned_undecided = [r for r in planned_alignments if not r.get("external_source") and r["decision"] == "undecided"]
    planned_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in planned_new:
        group = alignment_group(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        planned_groups[group].append(row)
    mapped_groups = 0
    mapped_candidates = 0
    for group, rows in planned_groups.items():
        mapped = [r for r in rows if r.get("ku_id")]
        if mapped:
            ids = {r["ku_id"] for r in mapped}
            assert len(ids) == 1 and len(mapped) == len(rows), (group, ids, len(mapped), len(rows))
            mapped_groups += 1
            mapped_candidates += len(rows)
    assert (len(planned_same), len(planned_new), len(planned_undecided)) == (1673, 5007, 5619)
    assert len(planned_groups) == 4830, len(planned_groups)
    assert (mapped_groups, mapped_candidates) == (48, 53), (mapped_groups, mapped_candidates)

    if args.dry_run:
        print(
            "dry-run passed:",
            f"groups={len(FAMILY_GROUPS)}",
            f"candidate_mappings={len(target_candidate_ids)}",
            f"S3_crosswalk_changes={len(CROSSWALK)}",
            f"new_candidates={len(planned_new)}",
            f"new_groups={len(planned_groups)}",
            f"registered_groups={mapped_groups}",
            f"registered_candidates={mapped_candidates}",
            f"manifest_after={len(manifest) + len(FAMILY_GROUPS)}",
        )
        return 0

    # All candidate, source quote, group, card path, and register checks above pass before writes begin.
    for record in FAMILY_GROUPS:
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
    new_accepted = [
        f"- 04-knowledge/units/families/{record['slug']}.md"
        for record in FAMILY_GROUPS
    ]
    accepted_lines[insert_at:insert_at] = new_accepted
    accepted_path.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    print(
        f"applied {len(FAMILY_GROUPS)} family identity groups and {len(target_candidate_ids)} candidate mappings; "
        f"reconciled {len(CROSSWALK)} cross-chapter candidate decisions; manifest={len(manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
