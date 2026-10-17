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
GROUP = "new-person:celotti-luigi-9757752530"
MEMBERS = ("cand-0622",)
KU_ID = "units/persons/luigi-celotti"
REL_PATH = "04-knowledge/units/persons/luigi-celotti.md"


RECORD = {
    "candidate": "cand-0622",
    "group": GROUP,
    "slug": "luigi-celotti",
    "name_zh": "路易吉·切洛蒂",
    "name_en": "Luigi Celotti",
    "description_zh": (
        "第16章称 Abate Luigi Celotti 是一位活跃于威尼斯、巴黎与伦敦的艺术品经销者，常建立并解散收藏；报纸上常出现转售艺术品的 discreet announcement。"
        "哈斯克尔称他经营的对象包括法国大革命期间从梵蒂冈教皇礼拜堂圣咏书取出的彩饰细密画、古代大师作品及18世纪威尼斯绘画，并据其描述推断他兼有销售才能与独立趣味。"
        "书中列其收藏中的八幅 Canaletto、Sebastiano Ricci 牧歌场景及 Tiepolo 素描。"
    ),
    "description_en": (
        "Chapter 16 describes Abate Luigi Celotti as an art dealer active in Venice, Paris, and London who repeatedly assembled and dispersed collections; newspaper notices often preceded his offers of works for sale. "
        "Haskell says the material he handled included illuminated miniatures taken from the Papal Chapel's Choral Books in the Vatican during the French Revolution, old masters, and eighteenth-century Venetian paintings, and infers from his descriptions both salesmanship and individual taste. "
        "The book lists eight Canalettos, a pastoral scene by Sebastiano Ricci, and Tiepolo sketches in his collection."
    ),
    "context_zh": (
        "人物主项为 `C.csv#146`，索引称 `Celotti, Abate Luigi`，对应第16章 p.377 的 `Abate Luigi Celotti`。本卡只记录来源明确的经销者身份与其收藏/交易语境；具体版画、绘画、拍卖目录和来源注释各自保持为作品或 archive 对象，不并入人物。"
    ),
    "context_en": (
        "The person main entry is `C.csv#146`, indexed as `Celotti, Abate Luigi`, corresponding to `Abate Luigi Celotti` in Chapter 16 (p. 377). This card records only the source-named dealer and his collection and trade context; individual prints, paintings, sale catalogues, and cited records remain separate work or archive objects."
    ),
    "boundary_zh": (
        "卡片依据本书第16章及其注释，不补写生卒年或外部身份核验。关于 Celotti 约1846年去世的注释转引 Levi，原书所引材料未独立查阅，故不将其提升为已核实生卒信息。来源仅称其经营或持有若干作品，不据此确定所有权、委托、盗取责任或单件作品身份；关系候选留待 S6，本卡未新增正式关系。"
    ),
    "boundary_en": (
        "This card relies on Chapter 16 and its notes and adds no birth or death dates or external identity check. The note's report that Celotti died around 1846 cites Levi, which was not independently consulted, so it is not promoted to verified life data. The source describes works he handled or held without resolving ownership, commissions, responsibility for removal, or the identity of individual works; relation candidates remain for S6, and no formal relations are added here."
    ),
    "sources": [
        card_writer.source(
            "16", "377", "16_CHP-16_intro.md", "48–64",
            "A much more adventurous and successful dealer",
            "哈斯克尔称 Abate Luigi Celotti 是比前述经销者更活跃且成功的艺术品经销者，并称其在共和国覆亡后仍生活约半世纪。",
            "保留作者在比较段落中的评价，不补写具体生卒年。",
        ),
        card_writer.source(
            "16", "377", "16_CHP-16_intro.md", "48–64",
            "Constantly building up collections and then dispersing them",
            "哈斯克尔称 Celotti 反复建立并散出收藏，活动见于 London、Paris 与其故乡 Venice。",
            "不据此推定完整旅行年表或固定居所。",
        ),
        card_writer.source(
            "16", "377", "16_CHP-16_intro.md", "48–64",
            "These were of all kinds and included",
            "哈斯克尔列举 Celotti 经手的对象，包括来自梵蒂冈教皇礼拜堂圣咏书的彩饰细密画，以及古代大师和18世纪威尼斯绘画。",
            "“taken from”是原文表述；不扩展为 Celotti 本人实施取走或其法律责任。",
        ),
        card_writer.source(
            "16", "377", "16_CHP-16_intro.md", "48–64",
            "It is legitimate to infer from his rhapsodic accounts",
            "哈斯克尔明确把销售才能与个人趣味表述为根据 Celotti 热情描述所作的推断。",
            "保留这是 Haskell 的推断，不当作外部评价或独立事实。",
        ),
        card_writer.source(
            "16", "377", "16_CHP-16_intro.md", "48–64",
            "Of his eight Canalettos",
            "哈斯克尔列出 Celotti 收藏中的八幅 Canaletto、Sebastiano Ricci 牧歌场景与 Tiepolo 素描。",
            "作品及数目沿用书中描述；未拆分或外部核验单件作品。",
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
    parser = argparse.ArgumentParser(description="Register the S4 Luigi Celotti person group")
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
    decisions = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    alignment_by_id = {row["candidate_id"]: row for row in decisions}
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")
    card_path = ROOT / REL_PATH

    manifest_matches = [row for row in manifest if row.get("ku_id") == KU_ID]
    accepted_registered = f"- {REL_PATH}" in accepted_text.splitlines()
    member_rows = [alignment_by_id[candidate_id] for candidate_id in MEMBERS]
    any_artifact = bool(manifest_matches) or card_path.exists() or accepted_registered or any(row.get("ku_id") == KU_ID for row in member_rows)
    if any_artifact:
        assert len(manifest) >= 1156
        assert len(manifest_matches) == 1 and manifest_matches[0].get("card_path") == REL_PATH
        assert card_path.exists() and accepted_registered
        assert all(row["decision"] == "new" and row.get("ku_id") == KU_ID for row in member_rows)
        assert all(f"S4 registration: mapped {GROUP} to {KU_ID}." in row["resolution_note"] for row in member_rows)
        card_text = card_path.read_text(encoding="utf-8-sig")
        assert "路易吉·切洛蒂（Luigi Celotti）" in card_text
        assert "created: '2026-10-16'" in card_text and "updated: '2026-10-16'" in card_text
        validate_sources(card_text)
        endpoint_ids, relation_ids = endpoint_counts(MEMBERS)
        assert (len(endpoint_ids), len(relation_ids)) == (26, 19)
        if args.dry_run:
            print(f"post-apply dry-run passed: Luigi Celotti card, accepted entry, candidate mapping, citations, and 26 endpoints / 19 relation candidates verified; manifest={len(manifest)}; no files written")
        else:
            print("already applied: Luigi Celotti S4 registration verified; no files written")
        return 0

    assert len(manifest) == 1155, f"unexpected manifest count: {len(manifest)}"
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
    assert (len(registered), sum(map(len, registered.values()))) == (136, 172)
    assert (len(person_groups), sum(map(len, person_groups.values()))) == (1087, 1179)
    assert (len(person_registered), sum(map(len, person_registered.values()))) == (30, 59)
    assert (len(person_groups) - len(person_registered), sum(map(len, person_groups.values())) - sum(map(len, person_registered.values()))) == (1057, 1120)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    candidate = candidate_by_id["cand-0622"]
    row = alignment_by_id["cand-0622"]
    assert candidate["suggested_type"] == KIND
    assert candidate["index_entry_id"] == "C.csv#146"
    assert candidate["canonical_name"] == "Celotti, Abate Luigi"
    assert row["decision"] == "new" and not row.get("ku_id") and get_group(row["resolution_note"]) == GROUP
    assert not card_path.exists(), f"unexpected existing card: {REL_PATH}"
    assert REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(row["type"] == KIND and "celotti" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for row in manifest)
    validate_sources()
    endpoint_ids, relation_ids = endpoint_counts(MEMBERS)
    assert (len(endpoint_ids), len(relation_ids)) == (26, 19), (len(endpoint_ids), len(relation_ids))

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
        print("dry-run passed: Luigi Celotti person_group=1 candidate_members=1 statement_endpoints=26 relation_candidates=19; no same-type KU or existing card; registered_groups_after=137 mapped_candidates_after=173 pending_groups=4683 pending_candidates=4816 manifest_after=1156; no files written")
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
    print(f"applied: Luigi Celotti person_groups=1 candidate_members=1 statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}; no formal relations added")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
