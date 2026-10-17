from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
UNITS = ROOT / "04-knowledge" / "units"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-16"
KIND = "person"
GROUP = "new-person:antonio-balestra-208aac65cb"
MEMBERS = ("cand-0168", "cand-0169")

RECORD = {
    "candidate": "cand-0168",
    "group": GROUP,
    "slug": "antonio-balestra",
    "name_zh": "安东尼奥·巴莱斯特拉",
    "name_en": "Antonio Balestra",
    "description_zh": (
        "Haskell 在第7至14章多次提及威尼斯画家 Antonio Balestra：他为 Schönborn 家族和 Buonaccorsi 收藏绘画，"
        "曾受到 Johann Wilhelm 邀请，并被 Algarotti 列入一项拟由法国与意大利画家合作的计划。"
        "本卡仅记录书中可证的姓名和职业语境，不补写生卒年、完整履历或外部身份。"
    ),
    "description_en": (
        "Across Chapters 7–14, Haskell names Antonio Balestra in the context of painting in Venice: he supplied pictures for the Schönborn family and the Buonaccorsi collection, "
        "was invited by Johann Wilhelm, and appeared in Algarotti’s proposed venture involving French and Italian painters. "
        "This card records only the name and professional contexts supported by the book, without adding dates, a full biography, or an externally verified identity."
    ),
    "context_zh": (
        "两个 S3 候选 cand-0168 与 cand-0169 的规范姓名均为 `Balestra, Antonio`，分别来自索引主项及不同章节／注释入口；"
        "S3 依据跨章正文全名 `Antonio Balestra` 将其归入同一人物组。第7章记 Schönborn 家族在 Pommersfelden 委托其绘画；"
        "第8章记他为 Buonaccorsi 的《埃涅阿斯纪》画廊绘制诗篇场景；第10章记 Johann Wilhelm 曾邀请他赴 Düsseldorf，"
        "脚注称他因珍视自由而拒绝定期任职；第14章将他列入 Algarotti 拟议的跨国合作计划。"
    ),
    "context_en": (
        "The two S3 candidates, cand-0168 and cand-0169, share the canonical index form `Balestra, Antonio` and arise from the index main entry and separate chapter or note locators. "
        "S3 grouped them by the full-name anchor `Antonio Balestra` across chapters. Chapter 7 records a Schönborn commission at Pommersfelden; Chapter 8 names him among painters "
        "who produced Aeneid scenes for the Buonaccorsi gallery; Chapter 10 reports Johann Wilhelm’s unsuccessful invitation to Düsseldorf and a footnote’s statement that Balestra "
        "declined regular employment because he valued his freedom; Chapter 14 includes him in Algarotti’s proposed collaborative venture."
    ),
    "boundary_zh": (
        "本卡只指 Haskell 书中具名的 Antonio Balestra。两条候选合并为一个人物 KU，不因索引页目或姓名重复再建副本；"
        "有关作品、委托、邀请和合作仍是关系端点，不在本轮写入正式关系。不同章节中的评价和注释保留各自语境；"
        "不据本书零散提及推定完整生平，也未作外部身份核验。"
    ),
    "boundary_en": (
        "This card identifies only the Antonio Balestra named in Haskell’s book. The two candidates map to one person KU; index locators and repeated mentions do not create duplicate people. "
        "Works, commissions, invitations, and collaboration remain relation endpoints and no formal relations are added in this registration. Chapter-specific judgments and notes retain their contexts. "
        "No complete biography or external identity is inferred."
    ),
    "sources": [
        card_writer.source(
            "7", "194", "07_CHP-7_sec_iv.md", "29–30",
            "commissioned pictures from Antonio Balestra and Gregorio Lazzarini in Venice",
            "第7章记 Schönborn 家族在 Pommersfelden 委托 Antonio Balestra 与 Gregorio Lazzarini 绘画。",
        ),
        card_writer.source(
            "8", "225", "08_CHP-8_sec_ii.md", "168–170",
            "Antonio Balestra in Venice",
            "第8章将 Balestra 列为在威尼斯为 Buonaccorsi 画廊绘制《埃涅阿斯纪》场景的画家之一。",
        ),
        card_writer.source(
            "10", "282", "10_CHP-10_intro.md", "147–150",
            "He also tried, albeit without success, to persuade Antonio Balestra",
            "第10章记 Johann Wilhelm 曾未能说服 Balestra 前往 Düsseldorf；同页脚注称他拒绝定期任职。",
        ),
        card_writer.source(
            "10", "289 n. 1", "10_CHP-10_intro_notes_p289_visual-transcription.md", "7",
            "Domenico Valeriani; Giuseppe Valeriani; Cimaroli; Balestra",
            "S2 对第289页注1表格的补充转录将 Balestra 列在 William III monument 项下；仅据该表记录列名。",
            "派生视觉转录，列项依照原 PDF 第18物理页；本轮未重新核对原页图像。",
        ),
        card_writer.source(
            "14", "351", "14_CHP-14_intro.md", "50–51",
            "along with Balestra and Donato Creti",
            "第14章记 Algarotti 将 Boucher 与 Balestra、Donato Creti 列入一项拟议的跨国合作计划；不据此命名具体作品。",
        ),
    ],
    "type_notes_zh": "中文显示名为便于识别所用工作音译；原书使用 Antonio Balestra。",
    "type_notes_en": "The Chinese display name is a working transliteration; the book uses Antonio Balestra.",
}


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the two-candidate Antonio Balestra person identity group")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    accepted = accepted_path.read_text(encoding="utf-8-sig")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert set(MEMBERS).issubset(candidate_by_id)
    assert {cid for cid, row in decisions.items() if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP} == set(MEMBERS)
    for cid in MEMBERS:
        row = decisions[cid]
        assert candidate_by_id[cid].get("suggested_type") == KIND
        assert candidate_by_id[cid].get("canonical_name") == "Balestra, Antonio"
        assert row.get("decision") == "new" and not row.get("ku_id")
        assert group_of(row.get("resolution_note", "")) == GROUP

    rel_path = f"04-knowledge/units/persons/{RECORD['slug']}.md"
    ku_id = f"units/persons/{RECORD['slug']}"
    card_path = ROOT / rel_path
    assert not card_path.exists() and rel_path not in accepted
    assert not any(row.get("ku_id") == ku_id or row.get("card_path") == rel_path for row in manifest)
    assert not any(
        row.get("type") == KIND
        and "antonio balestra" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )

    source_root = ROOT / "02-sources" / "02-Markdown"
    for item in RECORD["sources"]:
        source_text = " ".join((source_root / item["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in source_text, (item["file"], item["quote"])

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert len(direct) == 10 and len(relations) == 10, (len(direct), len(relations))

    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = ku_id
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {ku_id}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": ku_id,
        "type": KIND,
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": rel_path,
    })
    card_text = card_writer.make_card(RECORD, KIND)
    card_text, date_count = re.subn(
        r"^(created|updated): '2026-10-15'$", r"\1: '2026-10-16'", card_text, flags=re.MULTILINE
    )
    assert date_count == 2, f"expected two card dates, found {date_count}"
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", card_text, re.DOTALL)
    assert frontmatter and isinstance(yaml.safe_load(frontmatter.group(1)), dict), "generated card frontmatter is invalid"

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    process_append = (
        f"\n\n### S4 person：跨章人物直接端点身份组登记（{DATE}）\n\n"
        f"- `cand-0168,cand-0169` → `{GROUP}` → `{ku_id}`；10条直接 S2 断言，10条关系候选留待 S6。"
        "两条索引候选按跨章全名锚点归入同一人物；仅登记书中支持的画家身份与语境。"
        "未新增正式关系，未开展 S5 外部补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    result_append = (
        f"\n\n### S4 person：跨章人物直接端点身份组登记（{DATE}）\n\n"
        f"- cand-0168 与 cand-0169 共映射至[安东尼奥·巴莱斯特拉人物 KU](../units/persons/antonio-balestra.md)。"
        "卡片汇合第7、8、10、14章及第10章注释表中的姓名与职业语境；同组两个候选只建一张 KU。"
        "10条关系候选留待 S6，不新增正式关系。\n\n"
        f"本批新增1张人物 KU、2条候选映射。S4 当前已登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_process = process_text + process_append
    next_result += result_append

    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {ku_id}; candidates={len(MEMBERS)}; "
            f"source_quotes={len(RECORD['sources'])}; direct_statements={len(direct)}; "
            f"relation_candidates_pending={len(relations)}; registered={totals['registered_groups']}/"
            f"{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}"
        )
        return 0

    card_path.parent.mkdir(parents=True, exist_ok=True)
    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignments)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > rel_path),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {rel_path}")
    accepted_path.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {GROUP} -> {ku_id}; candidates={len(MEMBERS)}; "
        f"direct_statements={len(direct)}; relation_candidates_pending={len(relations)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
