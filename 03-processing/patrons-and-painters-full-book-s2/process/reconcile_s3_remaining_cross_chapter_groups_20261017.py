from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
CANDIDATES_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = "S3-cross-chapter-groups-2026-10-17"
OLD_TERM_GROUP = "sg3-term-pamfiligianbattistapopeinnocentx"
TERM_GROUPS = {
    "cand-1820": "sg3-term-pamfili-conservative-patronage",
    "cand-1822": "sg3-term-pamfili-retrenchment-effects",
}

CANDIDATE_DETAIL_UPDATES = {
    "cand-10117": "S3 cross-chapter review 2026-10-17: same work identity as index candidate cand-2859. The full title, A. M. Zanetti authorship, Venice publication, 1760 date, and p.345 visual-album context align. Keep the visual album distinct from archive citations to its publication.",
    "cand-10222": "S3 cross-chapter review 2026-10-17: same Dresden royal gallery institution as cand-9091, described under Pietro Guarienti and Augustus III. This identifies the gallery institution, not every collection or painting associated with it.",
    "cand-10279": "S3 cross-chapter review 2026-10-17: Villa Cordellina at Montecchio is the country house where Haskell says Tiepolo was decorating; same place identity as cand-8376. The source does not supply a separate formal building title.",
    "cand-11069": "S3 cross-chapter review 2026-10-17: the palace in Vicenza begun by Carlo Cordellina in 1770 is the Vicenza house described at p.160 as one of his two houses; same place identity as cand-8375. The source supplies no formal building title.",
    "cand-8375": "S3 cross-chapter review 2026-10-17: Haskell's p.160 Vicenza house is the palace in Vicenza begun by Carlo Cordellina in 1770 (cand-11069). Its formal building title is not given.",
    "cand-8376": "S3 cross-chapter review 2026-10-17: the Montecchio country house where Tiepolo decorated is named Villa Cordellina at p.352 (cand-10279); the two chapter anchors identify the same place.",
    "cand-2859": "S3 cross-chapter review 2026-10-17: the index subentry Varie Pitture a Fresco identifies the same 1760 visual album as body candidate cand-10117; keep the album as work, distinct from archive citations.",
    "cand-2876": "S3 cross-chapter review 2026-10-17: same work identity as body candidate cand-10111. The title Le Arti che vanno per via nella Città di Venezia and the Zompini context identify the visual print work.",
    "cand-10111": "S3 cross-chapter review 2026-10-17: same visual print work as index candidate cand-2876, Le Arti che vanno per via nella Città di Venezia. Haskell dates Zompini's drawings for it to 1753.",
    "cand-0879": "S3 cross-chapter review 2026-10-17: same Crespi painting as candidate cand-7720. Haskell says the picture was first described as Jupiter among the Corybantes and was sent under the title The Finding of Moses to reduce customs duty; the two titles are not separate works.",
    "cand-7720": "S3 cross-chapter review 2026-10-17: same Crespi painting as index candidate cand-0879. Haskell's p.405 postscript explains that the Jupiter/Corybantes commission was sent under the title The Finding of Moses; both names refer to one object.",
    "cand-3442": "S3 cross-chapter review 2026-10-17: the full-name Alexander the Great mentions align with cand-9593, including the represented historical figure in Pittoni's p.313 series. No additional title or biography is inferred.",
    "cand-9593": "S3 cross-chapter review 2026-10-17: the named subject Alexander the Great in Pittoni's p.313 series is the same person candidate as cand-3442. The represented figure is not merged with the painting/work object.",
    "cand-7116": "S3 cross-chapter review 2026-10-17: the bibliography's Bernardo de Dominici author form aligns with the index candidate cand-0942. The four-volume Vite is a separate archive object.",
    "cand-9182": "S3 cross-chapter review 2026-10-17: Giovanni Poleni in the p.301 correspondence account is the same person as index candidate cand-1968, Marchese Giovanni Poleni; no biography beyond the cited source is added.",
    "cand-9280": "S3 cross-chapter review 2026-10-17: Girolamo Zanetti in the Elogio note and p.360 citation is the same person as index candidate cand-2861. Keep distinct from A. M. Zanetti the Elder.",
    "cand-11166": "S3 cross-chapter review 2026-10-17: the p.401 Harris citation is identified by the p.425 bibliography byline as Enriqueta Harris and aligns with index candidate cand-1292. This is identity alignment only.",
    "cand-11371": "S3 cross-chapter review 2026-10-17: same archive volume as citation candidate cand-7251, volume III of Gli artisti italiani in Germania (Rome, 1943). Page-only citations at pp.282–283 remain unassigned to this volume.",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Finalize remaining cross-chapter S3 group boundaries by type.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment = sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = sync.read_csv(CANDIDATES_PATH)
    _, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_by_id = {
        row["candidate_id"]: row for row in alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    candidate_by_id = {row["candidate_id"]: row for row in candidates}

    expected_term_members = set(TERM_GROUPS)
    current_term_members = {
        row["candidate_id"] for row in alignment
        if row.get("candidate_id") and not row.get("external_source")
        and row["decision"] == "new"
        and sync.get_group(row.get("resolution_note", "")) == OLD_TERM_GROUP
    }
    assert current_term_members == expected_term_members
    assert all(candidate_by_id[cid]["suggested_type"] == "term" for cid in TERM_GROUPS)
    assert candidate_by_id["cand-1820"]["sub_entry"] == "conservative nature of patronage"
    assert candidate_by_id["cand-1822"]["sub_entry"] == "effect of economic retrenchment on artists"
    assert all(alignment_by_id[cid]["decision"] == "new" and not alignment_by_id[cid].get("ku_id") for cid in TERM_GROUPS)
    assert not any(row["type"] == "term" and row["canonical_name"] == "Pamfili, Gianbattista (Pope Innocent X)" for row in manifest)

    p_index = (ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "P.csv").read_text(encoding="utf-8-sig")
    ch5 = (ROOT / "02-sources" / "02-Markdown" / "05_CHP-5_sec_i.md").read_text(encoding="utf-8-sig")
    ch6 = (ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_i.md").read_text(encoding="utf-8-sig")
    ch8 = (ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md").read_text(encoding="utf-8-sig")
    ch20 = (ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md").read_text(encoding="utf-8-sig")
    assert "conservative nature of patronage" in p_index and "effect of economic retrenchment on artists" in p_index
    assert "the policy of economic retrenchment pursued by Innocent X" in ch5
    assert "financial troubles which afflicted Innocent’s reign" in ch6
    assert "The Infant\nJupiter handed over by Cybele to the Corybantes" in ch8
    assert "changed the title to The Finding of Moses" in ch8
    assert "cunningly described by him as The Finding of Moses" in ch20

    old_term_notes = {cid: alignment_by_id[cid]["resolution_note"] for cid in TERM_GROUPS}
    old_work_notes = {cid: alignment_by_id[cid]["resolution_note"] for cid in ("cand-0879", "cand-7720")}
    planned_alignment = [dict(row) for row in alignment]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid, group in TERM_GROUPS.items():
        sub = candidate_by_id[cid]["sub_entry"]
        planned_by_id[cid]["process_ref"] = PROCESS_REF
        planned_by_id[cid]["resolution_note"] = (
            f"source_ref=P.csv#{19 if cid == 'cand-1820' else 21}; parent_index=Pamfili, Gianbattista (Pope Innocent X); "
            f"sub_entry={sub}; group={group}; S3 cross-chapter review 2026-10-17: this subentry is a distinct term candidate, "
            "not the person named by the parent index heading. The 'conservative nature of patronage' and the 'effect of economic retrenchment on artists' "
            "are different concepts and have no shared term identity; keep separate new term groups. No same-type existing term KU matches either subentry. "
            f"The former shared group {OLD_TERM_GROUP} is withdrawn; prior grouping rationale is preserved in {PROCESS_REF}."
        )

    for cid, text in (
        ("cand-0879", "source_ref=chp-8:08_CHP-8_sec_ii:l206-214#L210; p.228 title and ch.20 p.405 postscript; group=workgrp-beb5c6c0eb0cbc; S3 cross-chapter review 2026-10-17: same painting as cand-7720. Haskell first records the Jupiter/Corybantes title and later explains that the same commission was sent as The Finding of Moses to reduce customs duty. Preserve both titles and the source's qualification; do not create two work identities. Prior rationale retained in process record."),
        ("cand-7720", "source_ref=chp-8:08_CHP-8_sec_ii:l126-138#L135; p.222 title; group=workgrp-beb5c6c0eb0cbc; S3 cross-chapter review 2026-10-17: same painting as cand-0879. Haskell's p.405 postscript says the Jupiter/Corybantes commission was sent under the title The Finding of Moses to reduce customs duty. Preserve both titles and the source's qualification; do not create two work identities. Prior rationale retained in process record."),
    ):
        planned_by_id[cid]["process_ref"] = PROCESS_REF
        planned_by_id[cid]["resolution_note"] = text

    planned_candidates = [dict(row) for row in candidates]
    planned_candidate_by_id = {row["candidate_id"]: row for row in planned_candidates}
    for cid, detail in CANDIDATE_DETAIL_UPDATES.items():
        assert cid in planned_candidate_by_id
        planned_candidate_by_id[cid]["detail"] = detail
    planned_candidate_by_id["cand-1820"]["detail"] = (
        "S3 keeps this term separate from cand-1822: the P.csv subentry concerns the conservative character of Innocent X's patronage, "
        "not the distinct economic-retrenchment effect on artists. The parent index name identifies the person as context, not the term itself."
    )
    planned_candidate_by_id["cand-1822"]["detail"] = (
        "S3 keeps this term separate from cand-1820: the P.csv subentry concerns the effect of Innocent X's economic retrenchment on artists, "
        "not the distinct concept of conservative patronage. The parent index name identifies the person as context, not the term itself."
    )

    stats = sync.summarize_by_type(planned_candidates, planned_alignment)
    totals = {key: sum(part[key] for part in stats.values()) for key in next(iter(stats.values()))}
    assert totals["new_candidates"] == 5009 and totals["new_groups"] == 4833
    assert totals["registered_groups"] == 422 and totals["pending_groups"] == 4411
    assert totals["pending_members"] == 4471

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    old_audit_detail = "含4,471条候选决定映射（4,410组）和15条外部身份记录。"
    assert result_text.count(old_audit_detail) == 1
    result_text = result_text.replace(
        old_audit_detail, "含4,471条候选决定映射（4,411组）和15条外部身份记录。"
    )
    marker = "\n\n### S3 跨章多候选身份组：分类型核对（2026-10-17）\n"
    assert result_text.count(marker) == 1
    result_text = result_text[:result_text.index(marker)] + (
        "\n\n### S3 跨章多候选身份组：分类型核对（2026-10-17）\n\n"
        "接续现有 alignment 记录，完成29个原跨章、多候选 `decision=new` 组的类型与身份边界核对。27组维持原组，2组拆分为四个独立身份组：Cardinal Angelo Cesi 与其兄弟 Monsignor Angelo Cesi；以及 Innocent X 索引下两个彼此不同的 term 子项。各候选的来源锚点、当前组号和变化理由见[对齐表](../tables/alignment.csv)及[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)。\n\n"
        "| 类型 | 原跨章多候选组数 | 当前处置 |\n|---|---:|---|\n"
        "| archive | 3 | 3组保留 |\n| institution | 1 | 1组保留 |\n| person | 16 | 15组保留；1组拆分 |\n"
        "| place | 2 | 2组保留 |\n| term | 4 | 3组保留；1组拆分 |\n| work | 3 | 3组保留 |\n"
        "| **合计** | **29** | **27组保留；2组拆分；形成31个new组** |\n\n"
        "术语拆分仅改 S3 identity grouping：`cand-1820` 与 `cand-1822` 共用的是人物索引主项，子项分别指向赞助保守性和经济紧缩影响，语义对象不同；两者各保留一个 new term 组。S4 已登记422组／538条映射，待登记4,411组／4,471条映射；S3 new=5,009个候选／4,833组；KU总数1,441。\n"
    )

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    assert "#s3-pamfili-term-subentry-split-20261017" not in process_text
    process_text += (
        "\n\n<a id=\"s3-pamfili-term-subentry-split-20261017\"></a>\n\n"
        "### S3 term／work／place：跨章候选身份复核与 Pamfili 子项拆分（2026-10-17）\n\n"
        "对29个原跨章多候选 new 组按类型核对：archive 3组、institution 1组、person 16组、place 2组、term 4组、work 3组。其余27组保持原 S3 组；本次新增一项 term 拆分，与前一节 Angelo Cesi 拆分合计2组拆分。结果分布见当前 results 与下表。\n\n"
        "| 类型 | 原组数 | 保留 | 拆分 | 拆分后涉及的当前组 |\n|---|---:|---:|---:|---:|\n"
        "| archive | 3 | 3 | 0 | 3 |\n| institution | 1 | 1 | 0 | 1 |\n| person | 16 | 15 | 1 | 17 |\n"
        "| place | 2 | 2 | 0 | 2 |\n| term | 4 | 3 | 1 | 5 |\n| work | 3 | 3 | 0 | 3 |\n"
        "| **合计** | **29** | **27** | **2** | **31** |\n\n"
        "P.csv#19 与 #21 的主项都是人物 `Pamfili, Gianbattista (Pope Innocent X)`，但候选类型为 term，子项分别是“conservative nature of patronage”和“effect of economic retrenchment on artists”。父级人物标题只提供索引语境，不证明两个术语是同一概念。故撤回共享组 `sg3-term-pamfiligianbattistapopeinnocentx`，`cand-1820` → `sg3-term-pamfili-conservative-patronage`，`cand-1822` → `sg3-term-pamfili-retrenchment-effects`；两者均为独立 new term，未匹配到同类型既有 KU。既有 `decline-of-roman-patronage` 是范围更广的章级概念，不作 same 映射。\n\n"
        "作品边界复核：`cand-0879` 与 `cand-7720` 同属 Crespi 一幅画。第8章 p.228 记录其 Jupiter/Corybantes 名称，p.222 与第二版后记 p.405 说明同一委托后来以 The Finding of Moses 之名送交以降低关税；两种题名保留为同一 work 的题名变化，不拆成两件作品。`cand-2859`／`cand-10117` 是同一 Zanetti 1760 视觉图册；`cand-2876`／`cand-10111` 是同一 Zompini 版画作品，沿用各自行 alignment group。\n\n"
        "地点边界复核：`cand-8375` 与 `cand-11069` 同指 Carlo Cordellina 在 Vicenza 的宅邸；p.160 的“两处住宅”定位与 p.143 开始建造的 Vicenza palace 相合。`cand-8376` 与 `cand-10279` 同指 Montecchio 的 Villa Cordellina，p.160 的 Tiepolo 装饰语境与 p.352 的具名地点相合；不补造建筑正式名称。Dresden Gallery 的机构组、其余跨章人物组及三组 archive 保留原 S3 决定和来源锚点。\n\n"
        "本次只更新 S3 group、候选 detail 与过程／结果记录；未更改 S2 statement 端点、`relations.csv` 或 S4 卡片。旧 term/work 对齐理由保留如下：\n\n"
        f"- `cand-1820`：{old_term_notes['cand-1820']}\n"
        f"- `cand-1822`：{old_term_notes['cand-1822']}\n"
        f"- `cand-0879`：{old_work_notes['cand-0879']}\n"
        f"- `cand-7720`：{old_work_notes['cand-7720']}\n\n"
        f"当前 S3 new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}；"
        f"S4已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条映射；KU总数{sync.fmt(len(manifest))}。"
    )

    if args.dry_run:
        print("Remaining cross-chapter S3 review dry-run passed")
        print("Pamfili term parent group split into cand-1820 and cand-1822 distinct term groups")
        print("Crespi title variants retained as one work; two place pairs and four other types retained")
        print(f"S3 new={totals['new_candidates']}/{totals['new_groups']}; pending S4={totals['pending_groups']}/{totals['pending_members']}")
        print(f"candidate detail updates={len(CANDIDATE_DETAIL_UPDATES) + 2}; previous term/work rationale preserved; no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    sync.write_csv(CANDIDATES_PATH, candidate_fields, planned_candidates)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: S3 new groups={totals['new_groups']}; pending S4={totals['pending_groups']}/{totals['pending_members']}; "
        f"candidate detail updates={len(CANDIDATE_DETAIL_UPDATES) + 2}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
