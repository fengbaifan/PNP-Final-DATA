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
KIND = "person"
GROUP = "new-person:antonio-zatta-d782464a1b"
MEMBERS = ("cand-2865",)
KU_ID = "units/persons/antonio-zatta"
REL_PATH = "04-knowledge/units/persons/antonio-zatta.md"


RECORD = {
    "candidate": "cand-2865",
    "group": GROUP,
    "slug": "antonio-zatta",
    "name_zh": "安东尼奥·扎塔",
    "name_en": "Antonio Zatta",
    "description_zh": (
        "第13章将 Antonio Zatta 列为18世纪威尼斯三位重要出版商之一。哈斯克尔称他在耶稣会争议中积极支持耶稣会，并曾因提议出版针对其对手的文本而与 Inquisitori 发生冲突；同时记述他出版的范围由礼仪小册子扩展至意大利经典，目录显示其为当时威尼斯多产的出版商。"
        "哈斯克尔称 Zatta 支持当时不流行的 Dante，并赞助一部相隔两个世纪才再现的插图版《神曲》；他写作的前言被评价为鲜明，常有机智讽刺。"
    ),
    "description_en": (
        "Chapter 13 lists Antonio Zatta among three important Venetian publishers of the eighteenth century. Haskell says he actively supported the Jesuits during political controversies and encountered the Inquisitori after proposing to publish texts attacking their opponents; his publishing ranged from ceremonial pamphlets to Italian classics, and his catalogues present him as a prolific publisher in Venice. "
        "Haskell says Zatta supported Dante when that view was unfashionable and sponsored an illustrated edition of the Commedia, the first to appear for two centuries; his prefaces are described as vivid and sometimes witty."
    ),
    "context_zh": (
        "人物主项为 `UVWXYZ.csv#202`，索引列出 pp.335、338、339。第13章 p.334 以全名将 Zatta 列入主要威尼斯出版商；p.338–339 再以全名及姓氏连续叙述其政治争议、出版活动与作品。第15章 p.367 注释中 `Zana` 的 OCR 经印本校为 `Zatta`，但该处是1787年一篇颂词的出版印记，不是完整人名锚点，本卡不依它确认个人身份。"
    ),
    "context_en": (
        "The person main entry is `UVWXYZ.csv#202`, indexed at pp. 335, 338, and 339. Chapter 13 (p. 334) names Zatta among major Venetian publishers; pp. 338–339 continue with his full name and surname in the account of political controversies, publishing activity, and books. In a Chapter 15 (p. 367) note, OCR `Zana` was corrected to `Zatta` from the print, but this is an imprint for a 1787 tribute, not a full personal-name anchor; this card does not rely on it to identify the person."
    ),
    "boundary_zh": (
        "卡片限于本书对出版商 Antonio Zatta 的称名与叙述，不补写生卒年或外部身份核验。关于同时代人称其为耶稣会平信徒成员的内容明确保留为转述；相关注释所引材料未独立查阅。作品、版次、书目记录与政治关系保持独立候选，不因出版行为自动登记关系；S2 关系候选留待 S6，本卡未新增正式关系。"
    ),
    "boundary_en": (
        "This card is limited to the book's account of publisher Antonio Zatta and adds no birth or death dates or external identity check. The statement that contemporaries regarded him as a lay member of the Society of Jesus remains explicitly reported; the cited materials in the note were not independently consulted. Works, editions, bibliographic records, and political ties remain separate candidates; publishing activity does not automatically create formal relations. S2 relation candidates remain for S6, and no formal relations are added here."
    ),
    "sources": [
        card_writer.source(
            "13", "334", "13_CHP-13_intro.md", "21–30",
            "Three publishers stand out above all the others",
            "哈斯克尔将 Antonio Zatta 与 Giambattista Albrizzi、Giambattista Pasquali 并列为突出的威尼斯出版商。",
        ),
        card_writer.source(
            "13", "338", "13_CHP-13_intro.md", "61–68",
            "The third of the greater Venetian publishers, Antonio Zatta",
            "哈斯克尔称 Zatta 是三位主要威尼斯出版商中的第三位，并叙述他在耶稣会争议中的立场及与 Inquisitori 的冲突。",
            "政治事件的细节保留 Haskell 的叙述范围。",
        ),
        card_writer.source(
            "13", "339", "13_CHP-13_intro.md", "70–77",
            "he himself was said by contemporaries to be a lay member",
            "哈斯克尔转述同时代人称 Zatta 为耶稣会平信徒成员。",
            "该句为转述；注释所引 Cattaneo 与 Nouvelles Ecclésiastiques 未独立查阅。",
        ),
        card_writer.source(
            "13", "339", "13_CHP-13_intro.md", "70–77",
            "A glance at his catalogues shows that Zatta was the most prolific publisher",
            "哈斯克尔据其目录称 Zatta 是18世纪威尼斯多产的出版商，并概述其出版意大利经典的活动。",
            "保留目录评价和作者归纳语气。",
        ),
        card_writer.source(
            "13", "339", "13_CHP-13_intro.md", "70–77",
            "Zatta was indeed a passionate supporter of Dante",
            "哈斯克尔称 Zatta 在相关观点不流行时仍积极支持 Dante，并赞助一部插图版作品。",
            "“two centuries”及“first”均为原书评价，未作外部书目核验。",
        ),
    ],
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


def get_group(note: str):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def endpoint_counts(member_ids):
    endpoint_ids = set()
    relation_ids = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if {statement.get("subject_candidate_id"), statement.get("object_candidate_id")} & set(member_ids):
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    return endpoint_ids, relation_ids


def validate_sources(card_text: str | None = None):
    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])
        if card_text is not None:
            assert item["quote"] in card_text, (REL_PATH, item["quote"])


def main():
    parser = argparse.ArgumentParser(description="Register the S4 Antonio Zatta person group")
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
    _, mentions = read_csv(TABLES / "mentions.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    alignment_by_id = {row["candidate_id"]: row for row in decisions}
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")
    card_path = ROOT / REL_PATH

    manifest_matches = [row for row in manifest if row.get("ku_id") == KU_ID]
    accepted_registered = f"- {REL_PATH}" in accepted_text.splitlines()
    member_rows = [alignment_by_id[candidate_id] for candidate_id in MEMBERS]
    any_artifact = bool(manifest_matches) or card_path.exists() or accepted_registered or any(row.get("ku_id") == KU_ID for row in member_rows)
    if any_artifact:
        assert len(manifest) >= 1157
        assert len(manifest_matches) == 1 and manifest_matches[0].get("card_path") == REL_PATH
        assert card_path.exists() and accepted_registered
        assert all(row["decision"] == "new" and row.get("ku_id") == KU_ID for row in member_rows)
        assert f"S4 registration: mapped {GROUP} to {KU_ID}." in member_rows[0]["resolution_note"]
        card_text = card_path.read_text(encoding="utf-8-sig")
        assert "安东尼奥·扎塔（Antonio Zatta）" in card_text
        assert "created: '2026-10-16'" in card_text and "updated: '2026-10-16'" in card_text
        validate_sources(card_text)
        endpoint_ids, relation_ids = endpoint_counts(MEMBERS)
        assert (len(endpoint_ids), len(relation_ids)) == (25, 16)
        if args.dry_run:
            print(f"post-apply dry-run passed: Antonio Zatta card, accepted entry, candidate mapping, citations, and 25 endpoints / 16 relation candidates verified; manifest={len(manifest)}; no files written")
        else:
            print("already applied: Antonio Zatta S4 registration verified; no files written")
        return 0

    assert len(manifest) == 1156, f"unexpected manifest count: {len(manifest)}"
    counts = Counter(row["decision"] for row in decisions)
    assert counts == Counter({"same": 1696, "new": 4989, "undecided": 5615, "excluded": 97, "conflict": 7})
    groups = defaultdict(list)
    registered = defaultdict(list)
    person_groups = defaultdict(list)
    person_registered = defaultdict(list)
    for row in decisions:
        if row["decision"] != "new":
            continue
        group = get_group(row["resolution_note"])
        assert group, f"new candidate lacks identity group: {row['candidate_id']}"
        groups[group].append(row)
        if candidate_by_id[row["candidate_id"]]["suggested_type"] == KIND:
            person_groups[group].append(row)
        if row.get("ku_id"):
            registered[group].append(row)
            if candidate_by_id[row["candidate_id"]]["suggested_type"] == KIND:
                person_registered[group].append(row)
    for group, rows in registered.items():
        assert len(rows) == len(groups[group]) and len({row["ku_id"] for row in rows}) == 1, group
    assert (len(groups), sum(map(len, groups.values()))) == (4820, 4989)
    assert (len(registered), sum(map(len, registered.values()))) == (137, 173)
    assert (len(person_groups), sum(map(len, person_groups.values()))) == (1087, 1179)
    assert (len(person_registered), sum(map(len, person_registered.values()))) == (31, 60)
    assert (len(person_groups) - len(person_registered), sum(map(len, person_groups.values())) - sum(map(len, person_registered.values()))) == (1056, 1119)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    candidate = candidate_by_id["cand-2865"]
    row = alignment_by_id["cand-2865"]
    assert candidate["suggested_type"] == KIND
    assert candidate["index_entry_id"] == "UVWXYZ.csv#202"
    assert candidate["canonical_name"] == "Zatta, Antonio"
    assert row["decision"] == "new" and not row.get("ku_id") and get_group(row["resolution_note"]) == GROUP
    assert not card_path.exists(), f"unexpected existing card: {REL_PATH}"
    assert REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(row["type"] == KIND and "zatta" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for row in manifest)
    imprint_mentions = [row for row in mentions if row.get("mention_id") == "m-chp15-p367-memmo-0060"]
    assert len(imprint_mentions) == 1
    assert imprint_mentions[0]["candidate_id"] == "cand-2865"
    assert imprint_mentions[0]["surface_form"] == "Zana" and "print reads Zatta" in imprint_mentions[0]["note"]
    validate_sources()
    endpoint_ids, relation_ids = endpoint_counts(MEMBERS)
    assert (len(endpoint_ids), len(relation_ids)) == (25, 16), (len(endpoint_ids), len(relation_ids))

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_by_id[MEMBERS[0]]["ku_id"] = KU_ID
    planned_by_id[MEMBERS[0]]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": KIND,
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": REL_PATH,
    })
    if args.dry_run:
        print("dry-run passed: Antonio Zatta person_group=1 candidate_members=1 statement_endpoints=25 relation_candidates=16; p.367 Zana/Zatta imprint is not treated as identity anchor; registered_groups_after=138 mapped_candidates_after=174 pending_groups=4682 pending_candidates=4815 manifest_after=1157; no files written")
        return 0

    card_text = card_writer.make_card(RECORD, KIND)
    card_text = re.sub(r"^created: '2026-10-15'$", "created: '2026-10-16'", card_text, flags=re.MULTILINE)
    card_text = re.sub(r"^updated: '2026-10-15'$", "updated: '2026-10-16'", card_text, flags=re.MULTILINE)
    assert "created: '2026-10-16'" in card_text and "updated: '2026-10-16'" in card_text
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
    print(f"applied: Antonio Zatta person_groups=1 candidate_members=1 statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}; p.367 imprint is not used as identity anchor; no formal relations added")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
