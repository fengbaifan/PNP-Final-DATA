from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
from collections import Counter
from pathlib import Path


ROOT = Path.cwd()
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
MANIFEST = TABLES / "ku-manifest.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_i.md"
BIBLIOGRAPHY = ROOT / "02-sources" / "02-Markdown" / "21_CHP-21Bibliography.md"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
PROCESS_REF = "S3-full-book-2026-10-16"
BACKUP_SUFFIX = ".bak-s3-brienne-inventories-20261016"

BRIENNE_GROUP = "archive-group-brienne-memoires-1916-1919"
INVENTORY_1653_GROUP = "archive-group-mazarin-inventory-1653"
DAUMALE_EDITION_GROUP = "archive-group-daumale-inventaire-1653-1861"
BNF_BRIENNE = "https://catalogue.bnf.fr/ark:/12148/cb340193395"
BNF_INVENTORY = "https://catalogue.bnf.fr/ark:/12148/cb30039849q"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), had_bom


def encode_csv(headers: list[str], rows: list[dict[str, str]], had_bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=headers, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    text = stream.getvalue()
    return ("\ufeff" + text if had_bom else text).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def group_from_note(note: str) -> str | None:
    match = re.search(r"(?:^|[; ])group=([^;\s]+)", note)
    return match.group(1) if match else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not (ROOT / "04-knowledge" / "accepted.yml").exists():
        raise SystemExit("Run this script from the project root.")

    alignment_headers, alignment, alignment_bom = read_csv(ALIGNMENT)
    candidate_headers, candidate_rows, candidate_bom = read_csv(CANDIDATES)
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    primary = [row for row in alignment if not row["external_source"]]
    external = [row for row in alignment if row["external_source"]]
    primary_by_id = {row["candidate_id"]: row for row in primary}
    if len(primary) != 12404 or len(alignment) != 12619 or len(external) != 215:
        raise SystemExit("Unexpected alignment shape; inspect the current S3 baseline.")
    expected = Counter({"same": 1768, "new": 5013, "undecided": 5516, "excluded": 99, "conflict": 8})
    if Counter(row["decision"] for row in primary) != expected:
        raise SystemExit("Unexpected S3 decisions; inspect the current baseline.")

    required_candidates = {"cand-6807", "cand-6814", "cand-7091", "cand-7071", "cand-7100", "cand-1596", "cand-1597"}
    if not required_candidates.issubset(candidate_by_id) or not required_candidates.issubset(primary_by_id):
        raise SystemExit("One or more expected source candidates are missing.")
    expected_types = {cid: "archive" for cid in required_candidates}
    if any(candidate_by_id[cid]["suggested_type"] != expected_types[cid] for cid in required_candidates):
        raise SystemExit("An expected archive candidate changed type; inspect before aligning.")
    if (candidate_by_id["cand-1596"]["index_entry_id"], candidate_by_id["cand-1596"]["sub_entry"]) != (
        "M.csv#135", "Brienne's account of farewell to his treasures"
    ):
        raise SystemExit("cand-1596 no longer identifies the expected index subentry.")
    if (candidate_by_id["cand-1597"]["index_entry_id"], candidate_by_id["cand-1597"]["sub_entry"]) != (
        "M.csv#136", "inventory of collection"
    ):
        raise SystemExit("cand-1597 no longer identifies the expected index subentry.")
    if candidate_by_id["cand-7091"]["canonical_name"] != "Inventory of Mazarin’s collection, 1661 (de Cosnac, item 1240)":
        raise SystemExit("cand-7091 no longer identifies the separately cited 1661 inventory.")

    for cid in ("cand-1596", "cand-1597", "cand-6814", "cand-6807"):
        if primary_by_id[cid]["decision"] != "undecided" or primary_by_id[cid]["ku_id"]:
            raise SystemExit(f"{cid} is no longer the expected undecided candidate.")
    if primary_by_id["cand-7071"]["decision"] != "new" or group_from_note(primary_by_id["cand-7071"]["resolution_note"]) != "archive-group-0282e4dee1c5":
        raise SystemExit("cand-7071 no longer has its expected volume-I group.")
    if primary_by_id["cand-7100"]["decision"] != "new" or group_from_note(primary_by_id["cand-7100"]["resolution_note"]) != "archive-group-a437079ba1fd":
        raise SystemExit("cand-7100 no longer has its expected volume-III group.")
    if primary_by_id["cand-7091"]["decision"] != "new" or group_from_note(primary_by_id["cand-7091"]["resolution_note"]) != "archive-group-fd76703203a6":
        raise SystemExit("cand-7091 no longer has its separate 1661-inventory group.")

    source_text = SOURCE.read_text(encoding="utf-8-sig")
    bibliography_text = BIBLIOGRAPHY.read_text(encoding="utf-8-sig")
    if "An inventory was at once drawn up" not in source_text or "the account given by Brienne of this occasion" not in source_text:
        raise SystemExit("Expected p.184/p.185 source anchors are missing.")
    if "Brienne, IH, pp. 88-90" not in source_text or "See the inventory of 1661 in de Cosnac, item 1240" not in source_text:
        raise SystemExit("The source does not contain the expected volume-III and 1661 locators.")
    if "Inventaire de tous les tneubles du Cardinal Mazarin dressé en 1653" not in bibliography_text:
        raise SystemExit("The D'Aumale bibliography entry changed; inspect before proceeding.")
    if "Mémoires, publiés par Paul Bonnefon, 3 vols." not in bibliography_text or "Paris 1916-19." not in bibliography_text:
        raise SystemExit("The Brienne bibliography entry does not identify the expected three-volume edition.")

    with MENTIONS.open("r", encoding="utf-8-sig", newline="") as stream:
        mentions = {row["mention_id"]: row for row in csv.DictReader(stream)}
    if mentions.get("m-chp7-p184-b-019", {}).get("candidate_id") != "cand-6814":
        raise SystemExit("The p.184 body inventory mention no longer maps to cand-6814.")

    with STATEMENTS.open("r", encoding="utf-8-sig") as stream:
        statement_rows = [json.loads(line) for line in stream if line.strip()]
    statements = {row["statement_id"]: row for row in statement_rows}
    expected_statements = {
        "st-chp7-p184-i04",
        "st-chp7-p184-n2-cite-daumale",
        "st-chp7-p184-n3-cite-inventory-cosnac",
        "st-chp7-p180-n2-cite-brienne",
        "st-chp7-p181-n1-cite-brienne",
        "st-chp7-p181-n2-cite-brienne",
        "st-chp7-p185-n5-cite-brienne",
    }
    if not expected_statements.issubset(statements):
        raise SystemExit("An expected S2 identity anchor is missing.")
    if statements["st-chp7-p184-n2-cite-daumale"]["qualifiers"].get("citation_publication_candidate_id") != "cand-6807":
        raise SystemExit("The p.184 note-2 publication mapping changed.")
    if statements["st-chp7-p184-n3-cite-inventory-cosnac"]["qualifiers"].get("citation_publication_candidate_id") != "cand-7091":
        raise SystemExit("The p.184 note-3 inventory mapping changed.")
    if statements["st-chp7-p185-n5-cite-brienne"]["qualifiers"].get("citation_publication_candidate_id") != "cand-7100":
        raise SystemExit("The p.185 note-5 Brienne volume mapping changed.")

    _, manifest, _ = read_csv(MANIFEST)
    for token in ("Inventaire de tous les meubles du cardinal Mazarin", "Inventory of Mazarin’s collection, 1653", "Mémoires de Louis-Henri de Loménie"):
        if any(row["type"] == "archive" and token.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for row in manifest):
            raise SystemExit(f"An accepted archive matching {token!r} now exists; compare it before keeping new groups.")

    if any(row["external_id"] in {BNF_BRIENNE, BNF_INVENTORY} for row in external):
        raise SystemExit("One of the BnF identity records already exists; inspect before adding duplicates.")
    for group in (BRIENNE_GROUP, INVENTORY_1653_GROUP, DAUMALE_EDITION_GROUP):
        if any(group_from_note(row["resolution_note"]) == group for row in primary):
            raise SystemExit(f"The new group {group!r} already exists.")

    updated_alignment = [dict(row) for row in alignment]
    updated_by_id = {row["candidate_id"]: row for row in updated_alignment if not row["external_source"]}

    old_6807 = updated_by_id["cand-6807"]["resolution_note"]
    old_6814 = updated_by_id["cand-6814"]["resolution_note"]
    old_1596 = updated_by_id["cand-1596"]["resolution_note"]
    old_1597 = updated_by_id["cand-1597"]["resolution_note"]
    old_7071 = updated_by_id["cand-7071"]["resolution_note"]
    old_7100 = updated_by_id["cand-7100"]["resolution_note"]

    updated_by_id["cand-6807"].update(
        decision="new",
        process_ref=PROCESS_REF,
        resolution_note=(
            f"source_ref=candidate_ref=chp-7:07_CHP-7_sec_i:l160-168#L168; "
            "statements=st-chp7-p183-n2-cite-daumale,st-chp7-p184-n2-cite-daumale; "
            f"group={DAUMALE_EDITION_GROUP}; external_identity=BnF Catalogue général FRBNF30039849, {BNF_INVENTORY}; "
            "The printed bibliography identifies the cited publication as Duc d’Aumale, Inventaire de tous les meubles du Cardinal Mazarin, drawn up in 1653 and published in London in 1861. The BnF record confirms the title, author, publication, date, and that it was published after the Condé original. "
            "This group denotes the 1861 printed edition, not the underlying inventory manuscript (cand-6814), nor the separate 1661 inventory cited in note 3 (cand-7091). The cited pages were not independently read; this decision aligns the bibliographic identity only. "
            f"prior_resolution_note={old_6807}"
        ),
    )
    updated_by_id["cand-6814"].update(
        decision="new",
        process_ref=PROCESS_REF,
        resolution_note=(
            f"source_ref=candidate_ref=chp-7:07_CHP-7_sec_i:l170-176#L172; "
            "mention=m-chp7-p184-b-019; statements=st-chp7-p184-i04,st-chp7-p184-n2-cite-daumale; "
            f"identity_peers=cand-1597; group={INVENTORY_1653_GROUP}; external_identity=BnF Catalogue général FRBNF30039849, {BNF_INVENTORY}; "
            "The p.184 body identifies an inventory drawn up when Mazarin returned to power in 1653, and note 2 cites d’Aumale’s 1861 publication, whose title identifies the 1653 inventory and says it was published from the Condé original. The BnF record describes that edition and identifies the original manuscript context (Musée Condé, Ms. 1294). "
            "The note-3 locator is a separate 1661 inventory (cand-7091), not a conflicting date for this body-referenced item. The source does not establish all historical details independently; this group records the inventory identity as reported and cited by Haskell. "
            f"prior_resolution_note={old_6814}"
        ),
    )
    updated_by_id["cand-1597"].update(
        decision="new",
        process_ref=PROCESS_REF,
        resolution_note=(
            "source_ref=index_entry=M.csv#136;page=184; body_candidate=cand-6814; "
            "body_mention=m-chp7-p184-b-019; statement=st-chp7-p184-i04; "
            f"identity_peers=cand-6814; group={INVENTORY_1653_GROUP}; "
            "The generic index subentry ‘inventory of collection’ points to the p.184 body phrase ‘An inventory was at once drawn up’; the associated note 2 and D’Aumale bibliography entry identify the 1653 inventory published from the Condé original. Keep the 1661 item in note 3 as separate candidate cand-7091. This is a same-group index locator, not a second archive identity. "
            f"prior_resolution_note={old_1597}"
        ),
    )
    updated_by_id["cand-1596"].update(
        decision="new",
        process_ref=PROCESS_REF,
        resolution_note=(
            "source_ref=index_entry=M.csv#135;pages=185-186; body_quote_lines=chp-7:07_CHP-7_sec_i:l215-222#L216-L218; "
            "statement=st-chp7-p185-n5-cite-brienne; citation_candidate=cand-7100; "
            f"identity_peers=cand-7071,cand-7100; group={BRIENNE_GROUP}; "
            "The index entry names Brienne’s farewell account; Haskell prints the passage on pp.185-186 and note 5 cites vol. III, pp.88-90. The bibliography and BnF Catalogue général identify the same 1916-1919 three-volume Mémoires edition edited by Paul Bonnefon; this passage is in volume III. Group it with the existing volume-I and volume-III citation candidates as one multivolume publication. "
            "Do not merge this archive with the person candidate for Brienne, nor treat the passage as a separate publication. The cited pages and quoted account were not independently checked against the edition; only bibliographic identity is aligned. "
            f"prior_resolution_note={old_1596}"
        ),
    )
    for cid, old_note, page_detail in (
        ("cand-7071", old_7071, "volume-I locators in p.180 n.2 and p.181 nn.1-2"),
        ("cand-7100", old_7100, "volume-III locator in p.185 n.5"),
    ):
        updated_by_id[cid].update(
            decision="new",
            process_ref=PROCESS_REF,
            resolution_note=(
                f"source_ref=prior_candidate={cid}; identity_peers=cand-7071,cand-7100,cand-1596; group={BRIENNE_GROUP}; "
                f"external_identity=BnF Catalogue général FRBNF34019339, {BNF_BRIENNE}; "
                f"The BnF record identifies Mémoires de Louis-Henri de Loménie, comte de Brienne, edited by Paul Bonnefon, as one three-volume Paris edition from 1916-1919. This candidate preserves its {page_detail} as volume/page locators within that set; it is not a separate edition or physical-volume identity. "
                "The cited pages were not independently consulted; the identity decision concerns the shared multivolume publication only. "
                f"prior_resolution_note={old_note}"
            ),
        )

    next_alignment_number = max(int(row["alignment_id"].split("-")[1]) for row in alignment) + 1
    external_rows = [
        {
            "alignment_id": f"aln-{next_alignment_number:04d}",
            "candidate_id": "cand-6807",
            "ku_id": "",
            "external_source": "BnF Catalogue général",
            "external_id": BNF_INVENTORY,
            "decision": "new",
            "accessed_date": "2026-10-16",
            "process_ref": PROCESS_REF,
            "legacy_ku_id": "",
            "resolution_note": "Identity only: BnF record FRBNF30039849 identifies Duc d’Aumale’s printed Inventaire de tous les meubles du cardinal Mazarin, London 1861, and describes it as published from the 1653 Condé original. This supports the printed edition identity, not its cited pages or all claims about the collection.",
        },
        {
            "alignment_id": f"aln-{next_alignment_number + 1:04d}",
            "candidate_id": "cand-6814",
            "ku_id": "",
            "external_source": "BnF Catalogue général",
            "external_id": BNF_INVENTORY,
            "decision": "new",
            "accessed_date": "2026-10-16",
            "process_ref": PROCESS_REF,
            "legacy_ku_id": "",
            "resolution_note": "Identity only: BnF record FRBNF30039849 titles the source inventory as drawn up in 1653 and says the 1861 edition was published from the original preserved in the Archives de Condé; its subject metadata identifies Musée Condé manuscript Ms. 1294. This supports the documentary identity distinction, not all historical claims in Haskell.",
        },
        {
            "alignment_id": f"aln-{next_alignment_number + 2:04d}",
            "candidate_id": "cand-7100",
            "ku_id": "",
            "external_source": "BnF Catalogue général",
            "external_id": BNF_BRIENNE,
            "decision": "new",
            "accessed_date": "2026-10-16",
            "process_ref": PROCESS_REF,
            "legacy_ku_id": "",
            "resolution_note": "Identity only: BnF record FRBNF34019339 identifies Louis-Henri de Loménie de Brienne’s Mémoires, edited by Paul Bonnefon, as a three-volume Paris edition dated 1916-1919. The record supports grouping volume-I and volume-III citations as locators within the same edition; it does not verify the cited passages.",
        },
    ]
    updated_alignment.extend(external_rows)

    updated_candidates = [dict(row) for row in candidate_rows]
    updated_candidate_by_id = {row["candidate_id"]: row for row in updated_candidates}
    updated_candidate_by_id["cand-6807"].update(
        canonical_name="Duc d’Aumale, Inventaire de tous les meubles du Cardinal Mazarin (London, 1861)",
        detail="The printed bibliography identifies the cited publication, its 1653 subject inventory, and London 1861 issue; BnF FRBNF30039849 confirms the title and publication. Haskell cites p.8 and pp.293 ff.; those pages were not independently read.",
    )
    updated_candidate_by_id["cand-6814"].update(
        canonical_name="Inventory of Mazarin’s collection drawn up in 1653 (as reported by Haskell)",
        detail="The p.184 body says an inventory was drawn up after Mazarin returned to power in 1653 and note 2 cites d’Aumale’s 1861 edition of the 1653 inventory. Note 3 separately cites the 1661 inventory in de Cosnac, item 1240 (cand-7091). BnF FRBNF30039849 identifies the printed edition and Condé original context; this candidate denotes the underlying 1653 inventory, not the 1861 book.",
    )

    result_text = RESULT.read_text(encoding="utf-8-sig")
    replacements = [
        ("new=5,013（4,833个身份组）", "new=5,017（4,834个身份组）"),
        ("undecided=5,516。S4 已登记281组、映射352条成员候选；尚待登记4,552组、4,661条映射。", "undecided=5,512。S4 已登记281组、映射352条成员候选；尚待登记4,553组、4,665条映射。"),
        ("| new | 5,013 | 按 4,833 个当前身份组进入 S4；每组登记一个 KU |", "| new | 5,017 | 按 4,834 个当前身份组进入 S4；每组登记一个 KU |"),
        ("| undecided | 5,516 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |", "| undecided | 5,512 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |"),
        ("| archive | 79→61 | 1,254／1,217 | 29／1,188；1,219 | 0 | 18 | 749 |", "| archive | 79→61 | 1,258／1,218 | 29／1,189；1,223 | 0 | 18 | 745 |"),
        ("| **合计** | **1,768→1,026** | **5,013／4,833** | **281／4,552；4,661** | **8** | **99** | **5,516** |", "| **合计** | **1,768→1,026** | **5,017／4,834** | **281／4,553；4,665** | **8** | **99** | **5,512** |"),
    ]
    for old, new in replacements:
        if result_text.count(old) != 1:
            raise SystemExit(f"Expected one result occurrence of {old!r}, found {result_text.count(old)}")
        result_text = result_text.replace(old, new, 1)
    result_section = (
        "### S3 archive：Brienne《Mémoires》卷级引用与 Mazarin 两份清单身份裁决（2026-10-16）\n\n"
        "- `cand-1596`（M.csv#135，pp.185–186）由 `undecided` 改为 `new`，与 `cand-7071`（卷 I 引文）及 `cand-7100`（卷 III 引文）同入 `archive-group-brienne-memoires-1916-1919`。第7章 p.185–186 刊出 Brienne 的告别叙述，注5定位卷 III、pp.88–90；第21章书目列 Bonnefon 编三卷本、Paris 1916–19。BnF 记录 FRBNF34019339 确认同一三卷版，因此卷 I、卷 III 是同一出版物的不同引用定位，索引所指段落并非独立出版物。人物候选 `cand-0452` 与此档案身份分开。\n"
        "- `cand-6807` 从 `undecided` 改为 `new`，身份组 `archive-group-daumale-inventaire-1653-1861`，表示 Duc d’Aumale 于1861年刊行的 *Inventaire de tous les meubles du Cardinal Mazarin*；`cand-6814` 与索引候选 `cand-1597` 同组 `archive-group-mazarin-inventory-1653`，表示正文所称1653年清单原件。第7章 p.184 正文将编制时间置于 Mazarin 1653 年复权后，注2定位 d’Aumale 出版物；书目全题为“dressé en 1653 … conservé dans les archives de Condé”。BnF FRBNF30039849 确认1861年版及其所据 Condé 原件。\n"
        "- 区分 p.184 注3另引 de Cosnac item 1240 的1661年清单（`cand-7091`，保留独立身份组 `archive-group-fd76703203a6`）；注3对应后文1653–1661年购入作品的叙述，不将1661误当作正文“An inventory”日期。原清单和 Brienne 引用页均未独立查阅；BnF 对齐只支持书目/文献身份，不验证 Haskell 的全部历史陈述。3条 BnF 外部身份记录见 `alignment.csv`；本轮不创建 KU、卡片或正式关系。"
    )
    marker = "### S4 按类型登记进度"
    if result_text.count(marker) != 1:
        raise SystemExit("Could not find the S4 type-progress insertion point.")
    result_text = result_text.replace(marker, result_section + "\n\n" + marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge_text += (
        "\n\n### S3 archive：Brienne《Mémoires》卷级引用与 Mazarin 两份清单身份裁决（2026-10-16）\n\n"
        "- `cand-1596`（M.csv#135，Brienne 告别藏品的叙述，pp.185–186）由 `undecided` 改为 `new`；与卷 I 引用候选 `cand-7071`、卷 III 引用候选 `cand-7100` 统一进入 `archive-group-brienne-memoires-1916-1919`。p.185–186 逐字刊出 Brienne 的第一人称记述，注5定位 `Mémoires`, vol. III, pp.88–90；21章书目确认 Paul Bonnefon 编三卷本、Paris 1916–19。BnF Catalogue général FRBNF34019339（https://catalogue.bnf.fr/ark:/12148/cb340193395）记录同一三卷本、责任者与出版时间，足以确认卷 I 和卷 III 引文属于一个多卷出版物身份。原卷页未独立阅读；裁决不验证引文本身。这里把卷号视为组内 locator，不把不同实体卷册声称为同一物理册。\n"
        "- `cand-6807`（d’Aumale 书目引文）由 `undecided` 改为 `new`，身份组 `archive-group-daumale-inventaire-1653-1861`；候选名称已规范为 Duc d’Aumale 的 *Inventaire de tous les meubles du Cardinal Mazarin*（London, 1861）。书目完整题名称该清单“dressé en 1653”且据 Condé 档案原件刊行；正文 p.183 注2、p.184 注2分别引该书 p.8 与 pp.293 ff.。BnF Catalogue général FRBNF30039849（https://catalogue.bnf.fr/ark:/12148/cb30039849q）确认作者、题名、Londres: Whittingham et Wilkins、1861，并记录所据 Condé 原件。组内对象是1861年刊本，不是底本清单。\n"
        "- `cand-6814`（p.184 正文所称1653年编制的藏品清单）由 `undecided` 改为 `new`，与索引候选 `cand-1597`（M.csv#136，p.184 `inventory of collection`）同属 `archive-group-mazarin-inventory-1653`。S2 mention `m-chp7-p184-b-019`、statement `st-chp7-p184-i04` 锚定“An inventory was at once drawn up”；note 2 引 d’Aumale 的1653清单刊本。该身份是 Haskell 所述清单原件的候选身份，历史事实不因目录记录而全量核实。候选表 `cand-6814` 从“date unresolved”更新为1653报告性身份，旧未决说明和索引候选原裁决保留在本记录及 alignment 的 `prior_resolution_note`。\n"
        "- 与上述1653清单区分：`cand-7091` 是注3所引 de Cosnac item 1240、明载1661年的独立清单，保留 `archive-group-fd76703203a6`。核对复合脚注映射后，注3对应1653至1661年间购藏的叙述；它不是正文“An inventory was at once drawn up”的日期证据。因此解决候选 `cand-6814` 原 alignment note 将注3说成“尚未迁移”导致的日期歧义。\n"
        "- 本次将 Brienne 与 d’Aumale/清单组映射至 BnF 权威目录，只新增3条 `external_source=BnF Catalogue général` 身份记录；无现有 archive KU 可复用，未创建 KU/card/manifest/relations。Brienne 的引文内容及原始清单未独立查阅；所有相关 S2 关系候选仍由 S6 审查。身份组证据和变化分别回链至 alignment、p.184/185 statements 与本记录。"
    )
    updates = {
        ALIGNMENT: encode_csv(alignment_headers, updated_alignment, alignment_bom),
        CANDIDATES: encode_csv(candidate_headers, updated_candidates, candidate_bom),
        RESULT: ("\ufeff" + result_text).encode("utf-8"),
        KNOWLEDGE: ("\ufeff" + knowledge_text).encode("utf-8"),
    }
    new_primary = [row for row in updated_alignment if not row["external_source"]]
    print("PREVIEW" if not args.apply else "APPLY")
    for path, content in updates.items():
        print(f"  {path.relative_to(ROOT)}: {sha256(path.read_bytes())} -> {sha256(content)}")
    print("  primary S3 decisions:", dict(Counter(row["decision"] for row in primary)), "->", dict(Counter(row["decision"] for row in new_primary)))
    print("  new identities: Brienne 3-volume edition group; 1653 inventory manuscript group; d’Aumale 1861 publication group")
    print("  external BnF identity rows: 3; S4 new groups +1; pending member mappings +4")
    if not args.apply:
        print("Dry-run only; pass --apply to write the changes.")
        return

    for path in updates:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"Recovery copy already exists: {backup}")
        shutil.copy2(path, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3-brienne-inventories-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied the archive identity decisions and retained recovery copies.")


if __name__ == "__main__":
    main()
