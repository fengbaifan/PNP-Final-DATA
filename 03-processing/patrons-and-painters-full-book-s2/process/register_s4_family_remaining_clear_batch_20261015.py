from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
UNITS = ROOT / "04-knowledge" / "units"
KIND = "family"


BATCH = [
    {
        "candidate": "cand-0824", "group": "sg3-family-cand-0824",
        "slug": "contarini-family-mira", "name_zh": "康塔里尼家族",
        "name_en": "Contarini family",
        "description_zh": "哈斯克尔称 Tiepolo 曾以 Contarini 家族1574年迎接法国国王 Henri III 访问 Mira 别墅的场景，表现该家族的辉煌时刻。此卡只登记书中所指家族集体。",
        "description_en": "Haskell says Tiepolo represented the Contarini family's 1574 welcome to Henri III of France at their villa in Mira as a moment of the family's greatest glory. This card registers only the collective family named in the book.",
        "context_zh": "第9章印刷页255将此家族置于威尼斯贵族以壁画彰显家族荣誉的语境。",
        "context_en": "Chapter 9 (p. 255) places the family in the context of Venetian nobles using frescoes to display family prestige.",
        "boundary_zh": "不补写具体支系、成员名册或家族沿革；迎接场景和壁画叙述尚未转为正式关系记录。",
        "boundary_en": "Do not add a branch, membership list, or family history; the welcome scene and fresco account have not been converted into formal relation records.",
        "sources": [card_writer.source("9", "255", "09_CHP-9_intro.md", "153", "In much the same way he painted the Contarini at the moment of their greatest glory—the welcome they gave in 1574 to Henri III of France when he visited their villa at Mira.", "哈斯克尔称 Tiepolo 以 Contarini 家族1574年在 Mira 别墅迎接 Henri III 的场景表现家族荣耀。")],
    },
    {
        "candidate": "cand-1706", "group": "sg3-family-cand-1706",
        "slug": "morosini-family-venice", "name_zh": "莫罗西尼家族",
        "name_en": "Morosini family",
        "description_zh": "哈斯克尔称 Morosini 是威尼斯十二个最古老家族之一，并说 Zenobio 购得的 Carmini 宫殿此前属于 Morosini。此处按书中集体家族称谓登记。",
        "description_en": "Haskell identifies the Morosini as one of Venice's twelve oldest families and says the Carmini palace bought by the Zenobio had previously belonged to the Morosini. The card registers the collective family named in the book.",
        "context_zh": "第9章印刷页250在叙述 Zenobio 家族及其宫邸时列出 Morosini。",
        "context_en": "Chapter 9 (p. 250) names the Morosini in the account of the Zenobio family and its palace.",
        "boundary_zh": "不据此确认具体出售者、交易日期或完整所有权链；该宫殿地点和相关正式关系分别审查。",
        "boundary_en": "Do not infer a particular seller, transaction date, or complete chain of title; the palace place and any formal relation are reviewed separately.",
        "sources": [card_writer.source("9", "250", "09_CHP-9_intro.md", "92", "The palace at the Carmini which they had bought from the Morosini, one of the twelve oldest families (the socalled Apostles)", "哈斯克尔称 Zenobio 购得的 Carmini 宫殿此前属于 Morosini，并称后者是十二个最古老家族之一。")],
    },
    {
        "candidate": "cand-8177", "group": "sg3-family-cand-8177",
        "slug": "pesaro-family-venice", "name_zh": "佩萨罗家族",
        "name_en": "Pesaro family",
        "description_zh": "哈斯克尔以 Pesaro 为例，称威尼斯旧家族拥有政治特权，并将其与以财富进入贵族阶层的新商人群体相对照。",
        "description_en": "Haskell cites the Pesaro as an old Venetian family with political privileges, contrasting them with new mercantile groups entering the aristocracy through wealth.",
        "context_zh": "第9章印刷页249讨论威尼斯贵族的财富、特权与新旧家族竞争。",
        "context_en": "Chapter 9 (p. 249) discusses wealth, privilege, and competition between old and new Venetian families.",
        "boundary_zh": "仅记录书中对 Pesaro 家族的集体称谓和政治特权概括，不将其扩展为个人传记或完整谱系。",
        "boundary_en": "Record only the collective Pesaro reference and the book's summary of its political privileges; do not expand it into individual biographies or a complete genealogy.",
        "sources": [card_writer.source("9", "249", "09_CHP-9_intro.md", "86", "Old families, like the Pesaro, had all the political privileges", "哈斯克尔以 Pesaro 家族说明威尼斯旧家族享有政治特权。")],
    },
    {
        "candidate": "cand-8386", "group": "sg3-family-cand-8386",
        "slug": "loredan-family-venice", "name_zh": "洛雷丹家族",
        "name_en": "Loredan family",
        "description_zh": "哈斯克尔称 Antonio Loredan 是 Loredan 家族的另一成员，并记其离开帕多瓦总督任期时被演说者比作 Pompey。该卡仅登记家族集体，不延伸为完整家族成员表。",
        "description_en": "Haskell calls Antonio Loredan another member of the Loredan family and says an orator compared him to Pompey as he left the governorship of Padua. This card registers only the family collective, not a complete membership list.",
        "context_zh": "第9章印刷页256将 Antonio 的离任演说与威尼斯贵族公共荣誉叙述相连。",
        "context_en": "Chapter 9 (p. 256) places Antonio's departure oration within the account of public honors for Venetian nobles.",
        "boundary_zh": "不将 Antonio 的政治任职或演说比较转写为其他 Loredan 家族成员的事实。",
        "boundary_en": "Do not transfer Antonio's office or the orator's comparison to other members of the Loredan family.",
        "sources": [card_writer.source("9", "256", "09_CHP-9_intro.md", "164", "another member of the Loredan family, Antonio, was, on leaving the governorship of Padua, compared to Pompey", "哈斯克尔称 Antonio 是 Loredan 家族成员，并记其离任时被比作 Pompey。")],
    },
    {
        "candidate": "cand-8589", "group": "sg3-family-cand-8589",
        "slug": "bonfiglioli-family-bologna", "name_zh": "邦菲廖利家族（博洛尼亚）",
        "name_en": "Bonfiglioli family in Bologna",
        "description_zh": "哈斯克尔在注释中称 Zaccaria Sagredo 从博洛尼亚的 Bonfiglioli 家族购得 Carracci 素描，并将该说法引至 Bottari。该卡只登记被点名的家族，不独立核验购藏史。",
        "description_en": "In a footnote, Haskell says Zaccaria Sagredo bought Carracci drawings from the Bonfiglioli family in Bologna and cites Bottari. This card registers the named family only; the collection history has not been independently checked.",
        "context_zh": "第9章印刷页263注5提供该家族称谓和书内引证；所引 Bottari 未独立查阅。",
        "context_en": "Chapter 9 (p. 263 n. 5) gives the family reference and Haskell's citation; Bottari was not independently consulted.",
        "boundary_zh": "不据此推定素描题名、家族成员、销售者个人身份或完整收藏流传链。",
        "boundary_en": "Do not infer drawing titles, family members, an individual seller, or a complete collection provenance from this citation.",
        "sources": [card_writer.source("9", "263 n. 5", "09_CHP-9_intro.md", "418", "He bought his Carracci drawings from the Bonfiglioli family in Bologna (Bottari, H, p. 186)", "哈斯克尔称 Zaccaria Sagredo 从博洛尼亚 Bonfiglioli 家族购得 Carracci 素描，并引 Bottari。", "原注转引 Bottari；未独立查阅被引文献。")],
    },
    {
        "candidate": "cand-10674", "group": "sg3-family-cand-10674",
        "slug": "venier-family-manfrin-property", "name_zh": "维涅尔家族",
        "name_en": "Venier family",
        "description_zh": "哈斯克尔称 Girolamo Manfrin 于1787年购得 Cannaregio 的古老 Venier 家族宫殿及其 Treviso 附近乡间宅邸。此处只登记家族集体和书中所述财产语境。",
        "description_en": "Haskell says Girolamo Manfrin bought the ancient Venier family's palace in Cannaregio and its country house near Treviso in 1787. This card registers only the family collective and the property context reported in the book.",
        "context_zh": "第17章 OCR L6 记述购置；前一页标 L8 仅显示 `[Page 3]`，下一处 L22 标记为 `[Page 381]`，本批暂按连续页序定位 p.380，待页图复核。",
        "context_en": "Chapter 17 OCR L6 reports the purchase. The preceding marker at L8 reads only `[Page 3]`, while L22 is marked `[Page 381]`; this batch provisionally locates the passage at p. 380 from page sequence, pending image review.",
        "boundary_zh": "不将该集体家族并入索引人物 Leonardo Venier；不推定具体售房者、分支或家族全部地产。页码暂定位性质已明示。",
        "boundary_en": "Keep this family collective separate from the indexed person Leonardo Venier; do not infer an individual seller, branch, or all family property. The provisional page location is explicitly marked.",
        "sources": [card_writer.source("17", "380", "17_CHP-17_sec_i.md", "6", "In 1787 he was in a position to buy the palace of the ancient family of Venier on the Cannaregio, as well as their country house near Treviso", "哈斯克尔称 Manfrin 于1787年购得 Venier 家族在 Cannaregio 的宫殿及其 Treviso 附近乡间宅邸。", "p.380 据连续页序暂定位：OCR L8 页标不完整，L22 为[Page 381]；待页图复核。")],
    },
]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note):
    match = re.search(r"group=([^;| ]+)", note)
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser(description="Register the six remaining clear S4 family groups")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_path = TABLES / "ku-manifest.csv"
    alignment_path = TABLES / "alignment.csv"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    manifest_fields, manifest = read_csv(manifest_path)
    alignment_fields, alignments = read_csv(alignment_path)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")
    assert len(manifest) == 1116, f"unexpected manifest count: {len(manifest)}"

    new_rows = [row for row in alignments if not row.get("external_source") and row.get("decision") == "new"]
    new_groups = defaultdict(list)
    registered = defaultdict(list)
    family_groups = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group
        new_groups[group].append(row)
        if row.get("ku_id"):
            registered[group].append(row)
        if candidate_by_id[row["candidate_id"]]["suggested_type"] == "family":
            family_groups[group].append(row)
    assert len(new_rows) == 5008 and len(new_groups) == 4831
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (97, 103)
    assert (len(family_groups), sum(map(len, family_groups.values()))) == (80, 85)
    family_registered = {group: rows for group, rows in registered_groups.items() if candidate_by_id[rows[0]["candidate_id"]]["suggested_type"] == "family"}
    assert (len(family_registered), sum(map(len, family_registered.values()))) == (68, 73)
    for group, rows in registered_groups.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(new_groups[group]) and len({row["ku_id"] for row in mapped}) == 1, group

    with (TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="") as f:
        mentioned = {row["candidate_id"] for row in csv.DictReader(f) if row.get("candidate_id")}
    candidate_endpoints = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as f:
        for line in f:
            statement = json.loads(line)
            candidate_endpoints.update(cid for cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")) if cid)
    assert len(BATCH) == 6 and len({row["candidate"] for row in BATCH}) == 6
    for record in BATCH:
        cid = record["candidate"]
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate["suggested_type"] == "family"
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert get_group(alignment["resolution_note"]) == record["group"]
        assert [row["candidate_id"] for row in new_groups[record["group"]]] == [cid]
        assert cid in mentioned or cid in candidate_endpoints
        rel_path = f"04-knowledge/units/families/{record['slug']}.md"
        ku_id = f"units/families/{record['slug']}"
        card_path = UNITS / "families" / f"{record['slug']}.md"
        assert not card_path.exists() and rel_path not in accepted_text
        assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
        for item in record["sources"]:
            source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
            assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (cid, item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest = list(manifest)
    new_paths = []
    for record in BATCH:
        cid = record["candidate"]
        ku_id = f"units/families/{record['slug']}"
        rel_path = f"04-knowledge/units/families/{record['slug']}.md"
        planned_by_id[cid]["ku_id"] = ku_id
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {record['group']} to {ku_id}."
        planned_manifest.append({"ku_id": ku_id, "type": "family", "canonical_name": record["name_zh"], "name_en": record["name_en"], "source_task": TASK, "card_path": rel_path})
        new_paths.append(rel_path)

    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if not row.get("external_source") and row.get("decision") == "new":
            planned_groups[get_group(row["resolution_note"])].append(row)
    planned_registered = {group: rows for group, rows in planned_groups.items() if any(row.get("ku_id") for row in rows)}
    for group, rows in planned_registered.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (103, 109)

    if args.dry_run:
        print("dry-run passed: family_groups=6 candidates=6 registered_groups_after=103 mapped_candidates_after=109 manifest_after=1122")
        return 0

    for record in BATCH:
        target = UNITS / "families" / f"{record['slug']}.md"
        target.write_text(card_writer.make_card(record, "family"), encoding="utf-8-sig", newline="\n")
    write_csv(manifest_path, manifest_fields, planned_manifest)
    write_csv(alignment_path, alignment_fields, planned_alignment)
    accepted_lines = accepted_text.splitlines()
    for rel_path in sorted(new_paths):
        insert_at = next((i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > rel_path), next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)))
        accepted_lines.insert(insert_at, f"- {rel_path}")
    accepted_path.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    print(f"applied: family_groups=6 candidates=6 manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

