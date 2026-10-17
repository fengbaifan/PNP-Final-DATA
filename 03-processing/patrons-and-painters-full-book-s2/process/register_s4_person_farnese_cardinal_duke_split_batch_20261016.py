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
CARDINAL_GROUP = "new-person:alessandro-farnese-b829378191"
DUKE_GROUP = "new-person:alessandro-farnese-duke-of-parma-cand-12426"
CARDINAL_ID = "units/persons/cardinal-alessandro-farnese"
DUKE_ID = "units/persons/alessandro-farnese-duke-of-parma"
CARDINAL_PATH = "04-knowledge/units/persons/cardinal-alessandro-farnese.md"
DUKE_PATH = "04-knowledge/units/persons/alessandro-farnese-duke-of-parma.md"
MEMBERS = {CARDINAL_GROUP: ("cand-0995",), DUKE_GROUP: ("cand-12426",)}
TRECCANI_URL = "https://www.treccani.it/enciclopedia/alessandro-farnese-duca-di-parma-piacenza-e-castro_(Dizionario-Biografico)/"
ULAN_URL = "http://vocab.getty.edu/page/ulan/500121936"
GOOGLE_BOOKS_URL = "https://books.google.com/books?id=EO8WSCkK8NYC"

RECORDS = {
    CARDINAL_GROUP: {
        "candidate": "cand-0995", "group": CARDINAL_GROUP, "slug": "cardinal-alessandro-farnese",
        "name_zh": "枢机亚历山德罗·法尔内塞", "name_en": "Cardinal Alessandro Farnese",
        "description_zh": (
            "哈斯克尔第3章称枢机亚历山德罗·法尔内塞以个人赞助主导罗马耶稣会 Gesù 教堂的建设；1568年接手赞助后，他指定 Vignola 为建筑师并任用自己的画家，"
            "把教堂视作个人与家族项目。第20章后记援引 Ackerman 时仍称其为支持 Vignola 的 Farnese camp 领袖。"
        ),
        "description_en": (
            "Chapter 3 describes Cardinal Alessandro Farnese as the personal patron behind the Jesuit church of the Gesù in Rome. After assuming its patronage in 1568, "
            "he employed Vignola as architect and his own painters, treating the church as a personal and family project. Chapter 20's postscript, reporting Ackerman, "
            "again names him as the Farnese-camp supporter of Vignola."
        ),
        "context_zh": (
            "索引主项 `F.csv#10` 原列 pp.65、66、69、78、84、137、398–400。第3章 Gesù 叙述与第20章后记均指枢机 Alessandro Farnese；索引列出的 p.137 实为低地国家战役人物，"
            "已依 S3 分拆至帕尔马公爵候选 `cand-12426`，不映射到本卡。"
        ),
        "context_en": (
            "The index main entry `F.csv#10` lists pp. 65, 66, 69, 78, 84, 137, and 398–400. The Chapter 3 Gesù account and Chapter 20 postscript refer to Cardinal Alessandro Farnese. "
            "The p. 137 index reference concerns the Low Countries campaign figure and was split in S3 to the Duke of Parma candidate `cand-12426`; it is not mapped to this card."
        ),
        "boundary_zh": (
            "本卡只指原书称为 Cardinal Alessandro Farnese 的枢机及艺术赞助人，与 Alessandro Farnese, Duke of Parma（cand-12426）严格区分。Getty ULAN 500121936 用于枢机身份消歧；"
            "不把外部身份记录扩展为对本书全部事实的核验。20条 S2 关系候选仍待 S6 逐项审查，本卡未新增正式关系。"
        ),
        "boundary_en": (
            "This card refers only to the cardinal and art patron Haskell calls Cardinal Alessandro Farnese, distinct from Alessandro Farnese, Duke of Parma (`cand-12426`). Getty ULAN 500121936 "
            "supports this identity distinction; it does not verify all claims in the book. All 20 S2 relation candidates remain for item-by-item S6 review. No formal relation is added here."
        ),
        "type_notes_zh": f"外部身份入口：[{ULAN_URL}]({ULAN_URL})（Getty ULAN 500121936；枢机、1520–1589）。仅用于身份对齐。",
        "type_notes_en": f"External identity record: [Getty ULAN 500121936]({ULAN_URL}) (cardinal, 1520–1589). Used for identity alignment only.",
        "sources": [
            card_writer.source("3", "65", "03_CHP-3_sec_ii.md", "3", "the most powerful of sixteenth-century Cardinals, Alessandro Farnese", "第3章明确以 Cardinal 身份称 Alessandro Farnese，并记其为 Gesù 教堂的赞助人。"),
            card_writer.source("3", "65", "03_CHP-3_sec_ii.md", "3–4", "His assumption of its patronage", "第3章叙述枢机接手 Gesù 教堂的赞助。"),
            card_writer.source("3", "65", "03_CHP-3_sec_ii.md", "4", "The Cardinal treated the new church as his private property", "第3章称枢机把新教堂视作私产；这是 Haskell 对其赞助方式的描述。"),
            card_writer.source("3", "65", "03_CHP-3_sec_ii.md", "4", "he employed his own architect Vignola and his own painters.", "第3章称枢机任用自己的建筑师 Vignola 与画家。"),
            card_writer.source("20", "398", "20_CHP-20Postscript.md", "35", "a Farnese camp, under Alessandro Cardinal Farnese, supporting Vignola.", "第20章后记援引 Ackerman 的论述，将 Alessandro Cardinal Farnese 与支持 Vignola 的 Farnese camp 相连。"),
        ],
    },
    DUKE_GROUP: {
        "candidate": "cand-12426", "group": DUKE_GROUP, "slug": "alessandro-farnese-duke-of-parma",
        "name_zh": "帕尔马公爵亚历山德罗·法尔内塞", "name_en": "Alessandro Farnese, Duke of Parma, Piacenza and Castro",
        "description_zh": (
            "哈斯克尔第5章称 Famiano Strada 的《De Bello Belgico》第二卷描绘 Alessandro Farnese 为西班牙一方进行的低地国家战役。原文未给其头衔；"
            "S3 依据 Treccani《意大利人传记辞典》及该卷题名，将其识别为帕尔马、皮亚琴察和卡斯特罗公爵 Alessandro Farnese。"
        ),
        "description_en": (
            "Chapter 5 says that the second volume of Famiano Strada's *De Bello Belgico* celebrates Alessandro Farnese's campaigns in the Low Countries on behalf of the Spaniards. "
            "Haskell does not give his title here. S3 identifies him as Alessandro Farnese, Duke of Parma, Piacenza and Castro, using Treccani's *Dizionario Biografico degli Italiani* "
            "and the title of Strada's second volume."
        ),
        "context_zh": (
            "第5章 p.137 在罗马西班牙赞助语境中提及该战役，并称 Strada 第二卷出版于1647年；这不表示战役发生于1647年。索引曾将 p.137 列在枢机条下，S3 已把该具名人物拆分为独立候选。"
        ),
        "context_en": (
            "Chapter 5 (p. 137) mentions the campaigns in its account of Spanish patronage in Rome and dates the illustrated second volume to 1647; this does not date the campaigns to 1647. "
            "The index placed p. 137 under the cardinal entry, but S3 split the named campaign figure into a separate candidate."
        ),
        "boundary_zh": (
            "本卡指低地国家战役语境中的 Alessandro Farnese，即帕尔马公爵；与枢机 Alessandro Farnese（cand-0995）不同。Treccani 与 Strada 题名只用于身份消歧，不把战役叙述的谓词或其他事实外推。"
            "该人物是1条 S2 关系候选的端点，留待 S6 审查；本卡未新增正式关系。"
        ),
        "boundary_en": (
            "This card identifies the Alessandro Farnese in the Low Countries campaign context as the Duke of Parma, distinct from Cardinal Alessandro Farnese (`cand-0995`). Treccani and Strada's title "
            "are used only to disambiguate identity, not to expand the source's predicates or other claims. He is the endpoint of one S2 relation candidate, retained for S6 review. No formal relation is added."
        ),
        "type_notes_zh": f"外部身份入口：[Treccani DBI](<{TRECCANI_URL}>)；[Famiano Strada《De Bello Belgico》第二卷目录记录](<{GOOGLE_BOOKS_URL}>)（1647，题名指向 Duke of Parma, Piacenza and Castro）。仅用于身份消歧。",
        "type_notes_en": f"External identity references: [Treccani DBI](<{TRECCANI_URL}>) and [the catalogue record for Strada's second volume](<{GOOGLE_BOOKS_URL}>) (1647 title identifies the Duke of Parma, Piacenza and Castro). Used for identity disambiguation only.",
        "sources": [
            card_writer.source(
                "5", "137", "05_CHP-5_sec_iii.md", "72–73",
                "the second volume of Famiano Strada’s De Bello Belgico, a celebration of Alessandro Farnese’s campaigns on behalf of the Spaniards in the Low\nCountries",
                "第5章称 Strada《De Bello Belgico》第二卷纪念 Alessandro Farnese 为西班牙一方进行的低地国家战役。",
                "Haskell 未在本段写明其头衔；身份据 S3 外部记录区分。",
            ),
        ],
    },
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
    parser = argparse.ArgumentParser(description="Register separate S4 cards for Cardinal and Duke Alessandro Farnese")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_path = TABLES / "ku-manifest.csv"
    alignment_path = TABLES / "alignment.csv"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    backlog_path = TABLES / "candidate-backlog.csv"
    manifest_fields, manifest = read_csv(manifest_path)
    alignment_fields, alignments = read_csv(alignment_path)
    backlog_fields, backlog = read_csv(backlog_path)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    current = decision_rows(alignments)
    alignment_by_id = {row["candidate_id"]: row for row in current}
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")

    assert len(manifest) == 1143
    assert len(candidates) == 12404 and len(alignments) == 12591
    decision_counts = Counter(row["decision"] for row in current)
    assert decision_counts == Counter({"same": 1696, "new": 4988, "undecided": 5616, "excluded": 97, "conflict": 7}), decision_counts
    groups = defaultdict(list)
    registered = defaultdict(list)
    for row in current:
        if row["decision"] == "new":
            group = get_group(row["resolution_note"])
            assert group, f"new candidate lacks group: {row['candidate_id']}"
            groups[group].append(row)
    for group, rows in groups.items():
        mapped = [row for row in rows if row.get("ku_id")]
        if mapped:
            assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
            registered[group] = rows
    assert (len(groups), sum(map(len, groups.values()))) == (4820, 4988)
    assert (len(registered), sum(map(len, registered.values()))) == (124, 155)
    assert (len(groups) - len(registered), sum(map(len, groups.values())) - sum(map(len, registered.values()))) == (4696, 4833)
    for group, members in MEMBERS.items():
        assert {row["candidate_id"] for row in groups[group]} == set(members)
        assert all(not row.get("ku_id") for row in groups[group])

    assert candidate_by_id["cand-0995"]["canonical_name"] == "Farnese, Cardinal Alessandro"
    assert candidate_by_id["cand-12426"]["canonical_name"] == "Farnese, Alessandro, Duke of Parma"
    assert get_group(alignment_by_id["cand-0995"]["resolution_note"]) == CARDINAL_GROUP
    assert get_group(alignment_by_id["cand-12426"]["resolution_note"]) == DUKE_GROUP
    assert alignment_by_id["cand-0995"]["decision"] == alignment_by_id["cand-12426"]["decision"] == "new"
    assert not any(row["type"] == KIND and "farnese" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for row in manifest)
    for rel_path, ku_id in ((CARDINAL_PATH, CARDINAL_ID), (DUKE_PATH, DUKE_ID)):
        assert rel_path not in accepted_text
        assert not any(row["card_path"] == rel_path or row["ku_id"] == ku_id for row in manifest)

    external_rows = {row["external_source"]: row for row in alignments if row.get("external_source") and row.get("candidate_id") in {"cand-0995", "cand-12426"}}
    assert set(external_rows) == {"Getty ULAN", "Treccani DBI"}
    assert not external_rows["Getty ULAN"]["ku_id"] and not external_rows["Treccani DBI"]["ku_id"]
    backlog = next(row for row in backlog if row["backlog_id"] == "bl-0002")
    assert backlog["candidate_id"] == "cand-12426" and backlog["status"] == "pending"

    statements = [json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    endpoint_counts = {}
    for cid, expected in (("cand-0995", (23, 20)), ("cand-12426", (1, 1))):
        endpoints = [row for row in statements if cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))]
        relation_rows = [row for row in endpoints if row.get("qualifiers", {}).get("relation_candidate") is True]
        endpoint_counts[cid] = (len(endpoints), len(relation_rows))
        assert endpoint_counts[cid] == expected, (cid, endpoint_counts[cid])
    campaign = next(row for row in statements if row["statement_id"] == "st-chp5-p137-farnese-named-as-campaign-leader")
    assert campaign["object_candidate_id"] == "cand-12426"

    for record in RECORDS.values():
        for item in record["sources"]:
            source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
            assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned_alignment)}
    for group, members in MEMBERS.items():
        ku_id = CARDINAL_ID if group == CARDINAL_GROUP else DUKE_ID
        for cid in members:
            planned_by_id[cid]["ku_id"] = ku_id
            planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {group} to {ku_id}."
    for row in planned_alignment:
        if row.get("alignment_id") == external_rows["Getty ULAN"]["alignment_id"]:
            row["ku_id"] = CARDINAL_ID
        elif row.get("alignment_id") == external_rows["Treccani DBI"]["alignment_id"]:
            row["ku_id"] = DUKE_ID

    planned_manifest = list(manifest)
    for group, ku_id, path, record in (
        (CARDINAL_GROUP, CARDINAL_ID, CARDINAL_PATH, RECORDS[CARDINAL_GROUP]),
        (DUKE_GROUP, DUKE_ID, DUKE_PATH, RECORDS[DUKE_GROUP]),
    ):
        planned_manifest.append({
            "ku_id": ku_id, "type": KIND, "canonical_name": record["name_zh"], "name_en": record["name_en"],
            "source_task": TASK, "card_path": path,
        })
    planned_backlog = [dict(row) for row in read_csv(backlog_path)[1]]
    duke_backlog = next(row for row in planned_backlog if row["backlog_id"] == "bl-0002")
    duke_backlog["status"] = "completed"
    duke_backlog["ku_id"] = DUKE_ID
    duke_backlog["decision_note"] = (
        "S1 candidate cand-12426 was registered in S4 as a separate person KU after S3 distinguished the Low Countries campaign figure "
        "from Cardinal Alessandro Farnese. Treccani DBI and the De Bello Belgico title support the identity distinction. The source-stated campaign relation remains for S6 review."
    )
    duke_backlog["process_ref"] = "S4-full-book-2026-10-16"

    if args.dry_run:
        print(
            "dry-run passed: separate Farnese person_groups=2 candidate_members=2 "
            f"cardinal_endpoints={endpoint_counts['cand-0995'][0]} cardinal_relation_candidates={endpoint_counts['cand-0995'][1]} "
            f"duke_endpoints={endpoint_counts['cand-12426'][0]} duke_relation_candidates={endpoint_counts['cand-12426'][1]} "
            "registered_groups_after=126 mapped_candidates_after=157 pending_groups=4694 pending_candidates=4831 "
            "manifest_after=1145 backlog_pending_after=0; no formal relations added"
        )
        return 0

    for group, path in ((CARDINAL_GROUP, CARDINAL_PATH), (DUKE_GROUP, DUKE_PATH)):
        record = RECORDS[group]
        card_text = card_writer.make_card(record, KIND)
        card_text, date_count = re.subn(
            r"^(created|updated): '2026-10-15'$", r"\1: '2026-10-16'", card_text, flags=re.MULTILINE
        )
        assert date_count == 2, f"expected two card dates in {path}, found {date_count}"
        (ROOT / path).write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(manifest_path, manifest_fields, planned_manifest)
    write_csv(alignment_path, alignment_fields, planned_alignment)
    write_csv(backlog_path, backlog_fields, planned_backlog)
    accepted_lines = accepted_text.splitlines()
    for rel_path in sorted((CARDINAL_PATH, DUKE_PATH)):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > rel_path),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {rel_path}")
    accepted_path.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    print(
        f"applied: separate Farnese person_groups=2 candidate_members=2 manifest={len(planned_manifest)} "
        "registered_groups=126 mapped_candidates=157 pending_groups=4694 pending_candidates=4831 backlog_pending=0; no formal relations added"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
