from __future__ import annotations

import argparse
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

KU_ID = "units/places/capuchin-church-rome"
GROUP = "sg3-ku-units-places-capuchin-church-rome"
RECONCILE = {
    "cand-0708": ("undecided", "sg3-place-cand-0708"),
    "cand-4521": ("new", "sg3-place-cand-4521"),
}
RELATION_IDS = {
    "st-chp2-secii-l127-139-antonio-decides-church",
    "st-chp2-secii-l127-139-capuchin-complex-site",
    "st-chp2-secii-l127-139-church-fashionable-patronage",
    "st-chp2-secii-l127-139-urban-foundation-visit-and-funding",
    "st-chp2-secii-l127-139-urban-patronage-confusion-s-maria",
    "st-chp2-secii-l141-145-barberini-decoration-responsibility-agreed",
    "st-chp2-secii-l141-145-barberini-nephews-decoration-role",
    "st-chp2-secii-l141-145-chapel-material-policy-agreed",
    "st-chp2-secii-l141-145-urban-special-dispensation",
    "st-chp2-seciv-l19-29-capuchin-introduction-forecast",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile S. Maria della Concezione index and body candidates to the accepted Roman Capuchin church KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}

    index_candidate = candidate_by_id["cand-0708"]
    body_candidate = candidate_by_id["cand-4521"]
    assert index_candidate["suggested_type"] == body_candidate["suggested_type"] == "place"
    assert index_candidate["index_entry_id"] == "C.csv#232"
    assert index_candidate["sub_entry"] == "S. Maria della Concezione"
    assert index_candidate["index_page_range"] == "42, 43"
    assert alignment_by_id["cand-0708"]["decision"] == "undecided"
    assert alignment_by_id["cand-4521"]["decision"] == "new"
    assert sync.get_group(alignment_by_id["cand-4521"].get("resolution_note", "")) == "sg3-place-cand-4521"
    assert any(row.get("ku_id") == KU_ID and row.get("card_path") == "04-knowledge/units/places/capuchin-church-rome.md" for row in manifest)
    assert "04-knowledge/units/places/capuchin-church-rome.md" in ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    chapter1 = (ROOT / "02-sources/02-Markdown/01_CHP-1_sec_ii.md").read_text(encoding="utf-8-sig")
    chapter2 = (ROOT / "02-sources/02-Markdown/02_CHP-2_sec_ii.md").read_text(encoding="utf-8-sig")
    index = (ROOT / "02-sources/03-Index/03-1-Index-MD/C.md").read_text(encoding="utf-8-sig")
    accepted_card = (ROOT / "04-knowledge/units/places/capuchin-church-rome.md").read_text(encoding="utf-8-sig")
    assert "for an altarpiece in the Capuchin church in Rome" in chapter1
    assert "the church of S. Maria della Concezione" in chapter2
    assert "for his Order a new church and monastery" in chapter2 and "on the Pincio" in chapter2
    assert "| Churches | Rome | S. Maria della Concezione |  | 42, 43 |" in index
    assert "Santa Maria della Concezione dei Cappuccini" in accepted_card
    assert "Dizionario-Biografico" in accepted_card
    relation_ids = {
        row["statement_id"] for row in sync.load_statements()
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and "cand-4521" in {row.get("subject_candidate_id"), row.get("object_candidate_id")}
    }
    assert relation_ids == RELATION_IDS

    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignments if row.get("candidate_id")}
    for cid, (prior_decision, prior_group) in RECONCILE.items():
        row = planned_by_id[cid]
        old_note = row.get("resolution_note", "")
        row["decision"] = "same"
        row["ku_id"] = KU_ID
        row["process_ref"] = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-capuchin-church-rome"
        row["resolution_note"] = (
            f"source_ref=chp-2:02_CHP-2_sec_ii:l127-139#L131;index_entry=C.csv#232;index_pages=42,43;"
            f"matched_manifest={KU_ID};matched_candidate_ids=cand-3494;group={GROUP}; "
            "S3 correction 2026-10-17: Haskell’s p.42 narrative names the church of S. Maria della Concezione and identifies its Capuchin-order foundation on the Pincio; the p.42–43 index sub-entry points to this same passage. The accepted Roman Capuchin church KU already records its identity as Santa Maria della Concezione dei Cappuccini. Treccani DBI vol. 89 records Andrea Sacchi’s public commissions at S. Maria della Concezione; see the [Treccani DBI entry](https://www.treccani.it/enciclopedia/andrea-sacchi_%28Dizionario-Biografico%29/) (accessed 2026-10-17). Haskell ch.1 p.12 calls the intended Capuchin church in Rome without its formal name. Reuse the accepted same-type place KU; do not duplicate the church. Keep the adjoining monastery candidate cand-4522 separate. "
            f"prior_decision={prior_decision};prior_group={prior_group};prior_resolution_note={old_note}"
        )

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    old_audit = "审计警告中的4,558条待登记 `decision=new` alignment 行，含4,543条候选决定映射（4,473组）和15条外部身份记录。"
    new_audit = "审计警告中的4,557条待登记 `decision=new` alignment 行，含4,542条候选决定映射（4,472组）和15条外部身份记录。"
    assert old_audit in result_text
    result_text = result_text.replace(old_audit, new_audit, 1)
    result_text += (
        "\n\n### S3 place：S. Maria della Concezione 复用既有罗马嘉布遣会教堂 KU（2026-10-17）\n\n"
        "候选 `cand-4521`（第2章 p.42 正文）和索引子目 `cand-0708`（C.csv#232，pp.42–43）现均由原 `new`／`undecided` 改为 `same`，映射至既有[罗马嘉布遣会教堂卡](../units/places/capuchin-church-rome.md)。索引页码对应的正文明确称 S. Maria della Concezione 是为嘉布遣会建立的教堂；该名称与既有卡已记录的 Santa Maria della Concezione dei Cappuccini 身份一致。相邻修道院候选 `cand-4522` 保持独立。10条直接关系候选不变，未创建新 KU 或正式关系。"
        f"S3 same={sync.fmt(totals['same_candidates'])}、new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组、undecided={sync.fmt(totals['undecided'])}；S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(manifest))}。"
    )

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s3-capuchin-church-rome\"></a>\n\n### S3 更正：S. Maria della Concezione 复用既有罗马嘉布遣会教堂 KU（2026-10-17）\n\n"
        "复核发现，第2章 p.42 正文候选 `cand-4521` 曾因“暂与既有罗马嘉布遣会教堂区分”的待核说明而登记为 `new`；索引候选 `cand-0708`（C.csv#232，子目 S. Maria della Concezione，pp.42–43）曾因缺少正文对应而列为 `undecided`。当前读取的第2章来源明确称 Urban VIII 与 Antonio Barberini 所涉地点为 S. Maria della Concezione，并称 Antonio 为嘉布遣会建立新教堂及修道院，位于 Pincio；索引页码正对应该段。\n\n"
        "已有 `units/places/capuchin-church-rome` 是同类型、已接受地点卡。卡片记录第1章 p.12 的 “Capuchin church in Rome”，并以 Treccani《意大利人传记辞典》对 Andrea Sacchi 于 S. Maria della Concezione 的公共委托记载，将罗马嘉布遣会教堂身份对应至 Santa Maria della Concezione dei Cappuccini。Treccani DBI 第89卷 Andrea Sacchi 条进一步列明 Sacchi 为该堂完成1633–35年的《圣安东尼的奇迹》及1636–37年的《圣博纳文图拉的幻视》。结合 Haskell 第1章与第2章的类型、城市和修会语境，p.42 的具名教堂与既有 KU 为同一地点。不是把教堂与修道院合并；`cand-4522` 修道院、index-only 的其他候选继续按各自状态处理。\n\n"
        "现将 `cand-4521` 由 `new` 更正为 `same`，将 `cand-0708` 由 `undecided` 更正为 `same`，两者均映射至 `units/places/capuchin-church-rome`；原决定、组号及完整理由保存在 alignment 的 `prior_decision`、`prior_group` 与 `prior_resolution_note` 文本中。该变更不新增 KU、manifest/accepted 条目或关系；10条直接 S2 关系候选保持原状。"
        f"S3 same={sync.fmt(totals['same_candidates'])}、new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组、conflict={sync.fmt(totals['conflict'])}、excluded={sync.fmt(totals['excluded'])}、undecided={sync.fmt(totals['undecided'])}。S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(manifest))}。"
    )

    if args.dry_run:
        print("S3 Capuchin church identity correction dry-run passed")
        print("cand-0708: undecided -> same; cand-4521: new -> same")
        print(f"both -> {KU_ID}; 10 direct relation candidates remain unchanged")
        print(f"same={sync.fmt(totals['same_candidates'])}; new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}; undecided={sync.fmt(totals['undecided'])}")
        print(f"S4 registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}")
        print("no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: cand-0708 and cand-4521 -> {KU_ID}; no KU or relations created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
