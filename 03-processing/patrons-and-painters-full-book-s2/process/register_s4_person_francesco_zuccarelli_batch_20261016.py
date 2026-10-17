from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
UNITS = ROOT / "04-knowledge" / "units"
KIND = "person"
GROUP = "new-person:francesco-zuccarelli-f14976b723"
MEMBERS = ("cand-2879", "cand-2884")
KU_ID = "units/persons/francesco-zuccarelli"
REL_PATH = "04-knowledge/units/persons/francesco-zuccarelli.md"

RECORD = {
    "candidate": "cand-2879",
    "group": GROUP,
    "slug": "francesco-zuccarelli",
    "name_zh": "弗朗切斯科·祖卡雷利",
    "name_en": "Francesco Zuccarelli",
    "description_zh": (
        "哈斯克尔称弗朗切斯科·祖卡雷利为风景画家，早年受到威尼斯画家安东尼奥·玛丽亚·扎内蒂赏识，并记其曾在英国长期工作、" 
        "为英国领事约瑟夫·史密斯作画。第13章称阿尔布里齐曾赞助他；第14章记述阿尔加罗蒂为他提出风景画题材。"
        "上述职业、赞助和委托内容均限于书内叙述。"
    ),
    "description_en": (
        "Haskell identifies Francesco Zuccarelli as a landscape painter, admired early in his career by the Venetian painter A. M. Zanetti, "
        "and recounts his extended work in England and painting for Consul Joseph Smith. Chapter 13 says Albrizzi patronized him; Chapter 14 "
        "describes Algarotti proposing a landscape subject for him. These career, patronage, and commission accounts remain bounded to the book."
    ),
    "context_zh": (
        "索引主项 UVWXYZ.csv#216 汇集第9、10、13、14、15、19章等页码；子目 UVWXYZ.csv#221“work in England”对应第10章 p.292，"
        "与主项及正文中的 Francesco Zuccarelli 同属一人。第10章 p.292 记其1752年赴英并在英国长期工作；p.308 记其为 Smith 作画及参与建筑组画；" 
        "第13章 p.342 回述 Zanetti 对其早期职业的赏识，第14章 p.351 记述 Algarotti 为他提议绘画题材。第19章 p.393 的销售清单将若干风景画列为 Zuccarelli 作，" 
        "但原文仅称它们据说来自 Smith 收藏。"
    ),
    "context_en": (
        "The main index entry UVWXYZ.csv#216 gathers pages from Chapters 9, 10, 13, 14, 15, and 19. The subentry UVWXYZ.csv#221, “work in England,” "
        "points to Chapter 10 p. 292 and belongs to the same person named Francesco Zuccarelli in the main entry and prose. Chapter 10 p. 292 dates his move to England to 1752 "
        "and describes an extended stay; p. 308 discusses his work for Smith and a series of architectural overdoors. Chapter 13 p. 342 recalls Zanetti's early admiration; "
        "Chapter 14 p. 351 describes Algarotti proposing a subject for him. Chapter 19 p. 393 lists landscapes attributed to Zuccarelli in a sale of pictures said to have come from Smith's collection."
    ),
    "boundary_zh": (
        "本卡只指书中明确全名为 Francesco Zuccarelli 的风景画家；不把“work in England”子目当作另一人物，也不凭姓氏或同一收藏语境扩展其他人物。" 
        "第10章说明 Smith 与 Zuccarelli 初次接触的时间不明，且 Zuccarelli 在某组建筑画中的分工较小；第19章销售目录的作品归属和 Smith 收藏来源均有原文限定。" 
        "候选 cand-2879、cand-2884 共对应21条直接 S2 断言端点，其中17条标为关系候选，均待 S6 逐项审查。本批不建立正式关系、具体作品 KU 或外部身份记录，也不作 S5 补足。"
    ),
    "boundary_en": (
        "This card refers only to the landscape painter whom the book names as Francesco Zuccarelli. The “work in England” subentry is not a second person, "
        "and no other person is added on the basis of a shared surname or collection context. Chapter 10 says the date of Smith's first contact with Zuccarelli is uncertain "
        "and that Zuccarelli's contribution to one architectural picture series was minor; Chapter 19 qualifies both the sale-list attribution and the reported Smith provenance. "
        "Candidates cand-2879 and cand-2884 map to 21 direct S2 statement endpoints, 17 marked as relation candidates, all retained for item-by-item S6 review. "
        "This batch adds no formal relation, individual work KU, external identity record, or S5 enrichment."
    ),
    "sources": [
        card_writer.source(
            "10", "292", "10_CHP-10_intro.md", "268–277",
            "The career of the landscape painter Francesco Zuccarelli was even more successful.6\nHe arrived in England in 1752 and remained here for over fifteen years with one break of three.",
            "第10章以全名称其为风景画家，记其1752年赴英并在英国长期工作；原文对中断时长只写作 three，卡片不补时间单位。",
            "来源 OCR 的脚注标号与后句断行依原样保留。",
        ),
        card_writer.source(
            "10", "308", "10_CHP-10_intro.md", "456–466",
            "Francesco Zuccarelli was an established landscape painter, who worked a great deal for Smith",
            "第10章称 Zuccarelli 是成熟的风景画家，为 Smith 作画；同段明确说两人首次接触的时间不明。",
        ),
        card_writer.source(
            "10", "328", "10_CHP-10_sec_ii.md", "241–246",
            "Francesco Zuccarelli was called ‘non mai abbastanza lodato’ by the elder Zanetti as early as 1738",
            "第10章记年长的 Anton Maria Zanetti 至迟在1738年已称赞 Zuccarelli。",
            "意大利语称赞语保留原文；不据此补写具体师承。",
        ),
        card_writer.source(
            "13", "336", "13_CHP-13_intro.md", "41–50",
            "he patronised the landscape artists Francesco Zuccarelli",
            "第13章记 Giambattista Albrizzi 曾赞助风景画家 Francesco Zuccarelli。",
        ),
        card_writer.source(
            "13", "342", "13_CHP-13_intro.md", "98–105",
            "was a keen admirer of Canaletto and Zuccarelli at the very beginning of their careers.",
            "第13章称 Zanetti 在 Canaletto 与 Zuccarelli 职业早期就是两人的热心欣赏者。",
        ),
        card_writer.source(
            "14", "351", "14_CHP-14_intro.md", "46–53",
            "and this led to Zuccarelli being given a subject such as The Hunt of Meleager and Atalanta ‘or something else, either sad or cheerful, in which the story corresponds to the mood of the landscape where it takes place’",
            "第14章记述 Algarotti 为 Zuccarelli 提议《梅勒阿格与阿塔兰忒之猎》等与风景情绪相配的题材。",
            "该段属于对拟议绘画题材的叙述，不据此认定现存作品或确切完成情况。",
        ),
        card_writer.source(
            "19", "393", "19_CHP-19Appendix.md", "140–155",
            "landscapes by Marco Ricci and Zuccarelli",
            "第19章附录列出一份1789年销售清单中的 Ricci 与 Zuccarelli 风景画，Haskell 只称这些作品据说来自 Smith 收藏。",
            "保留销售目录归属及来源限定；不等同于已核实的 Smith 所有权或完整作品目录。",
        ),
    ],
    "type_notes_zh": (
        "姓名：正文与索引主项使用 Francesco Zuccarelli；第9章引文有 Zuccharelli 拼写，按来源形式保留。中文显示名为工作音译。"
    ),
    "type_notes_en": (
        "Name: the prose and main index entry use Francesco Zuccarelli; a Chapter 9 quotation has the spelling Zuccharelli, retained as a source form. "
        "The Chinese display name is a working transliteration."
    ),
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def decision_rows(rows):
    return [row for row in rows if row.get("candidate_id") and not row.get("external_source")]


def get_group(note):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser(description="Register the Francesco Zuccarelli person group")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_path = TABLES / "ku-manifest.csv"
    alignment_path = TABLES / "alignment.csv"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    card_path = UNITS / "persons" / "francesco-zuccarelli.md"
    manifest_fields, manifest = read_csv(manifest_path)
    alignment_fields, alignments = read_csv(alignment_path)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    current = decision_rows(alignments)
    alignment_by_id = {row["candidate_id"]: row for row in current}
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")

    assert len(manifest) == 1160, f"unexpected manifest count: {len(manifest)}"
    decision_counts = Counter(row["decision"] for row in current)
    assert decision_counts == Counter({"same": 1697, "new": 4988, "undecided": 5615, "excluded": 97, "conflict": 7}), decision_counts
    groups = defaultdict(list)
    registered = defaultdict(list)
    for row in current:
        if row["decision"] == "new":
            group = get_group(row["resolution_note"])
            assert group, f"new candidate lacks group: {row['candidate_id']}"
            groups[group].append(row)
            if row.get("ku_id"):
                registered[group].append(row)
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    for group, rows in registered_groups.items():
        assert len(rows) == len(groups[group]) and len({row["ku_id"] for row in rows}) == 1, group
    assert (len(groups), sum(map(len, groups.values()))) == (4819, 4988)
    assert (len(registered_groups), sum(len(rows) for rows in registered_groups.values())) == (141, 177)
    assert (len(groups) - len(registered_groups), sum(map(len, groups.values())) - sum(len(rows) for rows in registered_groups.values())) == (4678, 4811)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate["suggested_type"] == KIND
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert get_group(alignment["resolution_note"]) == GROUP
    assert candidate_by_id["cand-2879"]["canonical_name"] == "Zuccarelli, Francesco"
    assert candidate_by_id["cand-2879"]["index_entry_id"] == "UVWXYZ.csv#216"
    assert candidate_by_id["cand-2884"]["index_entry_id"] == "UVWXYZ.csv#221"
    assert candidate_by_id["cand-2884"]["sub_entry"] == "work in England"
    assert not card_path.exists() and REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(
        row["type"] == KIND and "zuccarelli" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )

    endpoint_ids = set()
    relation_ids = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if set(MEMBERS) & {statement.get("subject_candidate_id"), statement.get("object_candidate_id")}:
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert len(endpoint_ids) == 21 and len(relation_ids) == 17, (len(endpoint_ids), len(relation_ids))

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned_alignment)}
    planned_manifest = list(manifest)
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": KIND,
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": REL_PATH,
    })

    planned_groups = defaultdict(list)
    for row in decision_rows(planned_alignment):
        if row["decision"] == "new":
            planned_groups[get_group(row["resolution_note"])].append(row)
    planned_registered = {group: rows for group, rows in planned_groups.items() if any(row.get("ku_id") for row in rows)}
    for group, rows in planned_registered.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
    assert (len(planned_registered), sum(len(rows) for rows in planned_registered.values())) == (142, 179)
    assert (len(planned_groups) - len(planned_registered), sum(map(len, planned_groups.values())) - sum(len(rows) for rows in planned_registered.values())) == (4677, 4809)

    if args.dry_run:
        print(
            "dry-run passed: Francesco Zuccarelli person_groups=1 candidate_members=2 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            f"registered_groups_after={len(planned_registered)} mapped_candidates_after="
            f"{sum(len(rows) for rows in planned_registered.values())} pending_groups=4677 "
            f"pending_candidates=4809 manifest_after={len(manifest) + 1}; no formal relations added"
        )
        return 0

    card_text = card_writer.make_card(RECORD, KIND)
    card_text, date_count = re.subn(
        r"^(created|updated): '2026-10-15'$", r"\1: '2026-10-16'", card_text, flags=re.MULTILINE
    )
    assert date_count == 2, f"expected two card dates, found {date_count}"
    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(manifest_path, manifest_fields, planned_manifest)
    write_csv(alignment_path, alignment_fields, planned_alignment)
    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > REL_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {REL_PATH}")
    accepted_path.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    print(
        f"applied: Francesco Zuccarelli person_groups=1 candidate_members=2 statement_endpoints={len(endpoint_ids)} "
        f"relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}; no formal relations added"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
