from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
import register_s4_archive_memmo_query_sheet_20261017 as process_sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
GROUP = "archive-group-ff938f5595f2"
MEMBERS = ("cand-1532", "cand-5338")
KU_ID = "units/archives/jesuit-fondo-di-gesu-865-13-s-andrea-altarpiece-documents"
CARD_REL = "04-knowledge/units/archives/jesuit-fondo-di-gesu-865-13-s-andrea-altarpiece-documents.md"
NAME_ZH = "S. Andrea al Quirinale 祭坛画文书（耶稣会档案馆 Fondo di Gesù N. 865-13）"
NAME_EN = "Documents relating to the altarpieces at S. Andrea al Quirinale (Jesuit Archives, Fondo di Gesù, N. 865-13)"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
CH3_QUOTES = (
    "MSS. in Jesuit Archives: Fondo di Gesù—N. 865-13.",
    "ibid., Fondo di Gesù—N. 865-13. For the fidi text of Brandi’s letters to the Jesuit fathers see Appendix 1.",
    "ibid., Fondo di Gesù—N. 865-13. For Maratta’s dealings with the Jesuits see Appendix 1.",
)
APPENDIX_QUOTE = (
    "Documents relating to thè altarpieces in S. Andrea al Quirinale by Giacinto Brandi and Carlo\n"
    "Maratta in thè Jesuit Archives, Borgo S. Spirito, 5, Rome: Fondo di Gesù—N. 865-13. See\n"
    "Chapter 3, p. 88, notes 2 and 3."
)
RELATION_IDS = (
    "st-chp3-seciv-notes-l205-243-p88-n1-86513",
    "st-chp3-seciv-notes-l205-243-p88-n2-86513",
    "st-chp3-seciv-notes-l205-243-p88-n3-86513",
)
PROCESS_ANCHOR = "s4-jesuit-fondo-di-gesu-86513-20261017"
IDENTITY_SCOPE = (
    " S3 identity scope clarification (2026-10-17): both candidates share the printed citation locator "
    "Jesuit Archives, Fondo di Gesù, N. 865-13. The physical archival level, the number of constituent "
    "records, and the identity of individual records have not been independently verified; this KU records "
    "the locator and Haskell's descriptive subject, not a verified physical file or dossier."
)


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return " ".join(text.split())


def source_rows():
    return [
        {
            "citation": BOOK_CITATION,
            "location": "第3章，印刷页88，注1–3；Markdown 行228–230。档案原件及馆藏目录未独立查阅。",
            "sentence_summary": (
                "注1–3均引 Jesuit Archives, Fondo di Gesù, N. 865-13；注2指向附录1中 Brandi 致耶稣会士书信，"
                "注3指向 Maratta 与耶稣会士往来相关材料。"
            ),
            "original_quotes": [
                {"source_span": "line 228; print p. 88, note 1", "text": CH3_QUOTES[0]},
                {"source_span": "line 229; print p. 88, note 2", "text": CH3_QUOTES[1]},
                {"source_span": "line 230; print p. 88, note 3", "text": CH3_QUOTES[2]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
                "source_span": "lines 228–230; print p. 88, notes 1–3",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第19章附录1，印刷页386；Markdown 行5–7。档案原件及馆藏目录未独立查阅。",
            "sentence_summary": (
                "附录题注明确将相关文书描述为 Brandi、Maratta 在 S. Andrea al Quirinale 祭坛画的文件，"
                "定位于罗马 Jesuit Archives, Fondo di Gesù, N. 865-13，并回指第3章 p.88 注2、3。"
            ),
            "original_quotes": [
                {"source_span": "lines 5–7; print p. 386", "text": APPENDIX_QUOTE},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md",
                "source_span": "lines 5–7; print p. 386",
            },
        },
    ]


def card_text():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "archival locator",
        "evidence_status": "source_backed",
        "sources": source_rows(),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch3 = "../../../02-sources/02-Markdown/03_CHP-3_sec_iv.md"
    appendix = "../../../02-sources/02-Markdown/19_CHP-19Appendix.md"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔第19章附录1对 S. Andrea al Quirinale 祭坛画相关文书的描述及其档案定位：罗马 Jesuit Archives, Fondo di Gesù, N. 865-13。附录将文书与 Giacinto Brandi、Carlo Maratta 联系起来，并回指第3章 p.88 注2、注3；第3章注1–3均引同一编号。这里登记的是哈斯克尔所载定位号与描述，不认定原件的编目层级、实体卷宗边界或所含单件数量。原件与馆藏目录未在本轮查阅。

**English:** This card records Haskell’s description and citation locator for documents concerning the S. Andrea al Quirinale altarpieces: Jesuit Archives, Rome, Fondo di Gesù, N. 865-13. Appendix 1 associates the documents with Giacinto Brandi and Carlo Maratta and refers back to Chapter 3, p. 88, notes 2 and 3; notes 1–3 in Chapter 3 cite the same number. The KU represents the locator and description reported by Haskell. It does not establish the archival cataloguing level, the boundaries of a physical file or dossier, or the number of constituent records. Neither the archival originals nor a repository catalogue was consulted in this pass.

### 文献属性与范围

- **展示题名：** 依据哈斯克尔附录1的描述拟定，不声称是原件题名。
- **来源定位：** Jesuit Archives, Borgo S. Spirito, 5, Rome；Fondo di Gesù；N. 865-13。以上为哈斯克尔书内定位，本轮未核对档案机构现行名称、层级或目录记录。
- **书内描述范围：** 第19章附录1称相关文书涉及 Giacinto Brandi 与 Carlo Maratta 在 S. Andrea al Quirinale 的祭坛画；第3章注2、注3分别指向 Brandi 致耶稣会士书信和 Maratta 与耶稣会士往来相关材料。[第3章 p. 88](../../../{ch3})（L228–230）；[第19章附录1 p. 386](../../../{appendix})（L5–7）
- **身份边界：** 本卡对应 S3 身份组 `{GROUP}`，由候选 `cand-1532`（索引子目）与 `cand-5338`（正文档案定位候选）组成。两者共享相同书内定位号；档案实物的单件边界尚待原件或馆藏目录核实。该组与祭坛画作品候选、Brandi 与 Maratta 人物、以及 Jesuit Archives 机构本身分开。

## 关系与证据

第3章注1–3形成的直接 S2 关系候选（{', '.join(RELATION_IDS)}）均留待 S6 逐条核对端点、方向、语境与证据；本卡登记不把书内引注转换成正式关系，也不确认原件内容。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Jesuit Archives N. 865-13 citation locator in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decision_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decision_by_id) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert all(cid in candidate_by_id for cid in MEMBERS)
    group_members = {
        cid for cid, row in decision_by_id.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    for cid in MEMBERS:
        assert candidate_by_id[cid].get("suggested_type") == "archive"
        assert decision_by_id[cid].get("decision") == "new" and not decision_by_id[cid].get("ku_id")

    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(row.get("type") == "archive" and NAME_EN.casefold() == (row.get("name_en") or "").casefold() for row in manifest)

    source_checks = (
        ("02-sources/02-Markdown/03_CHP-3_sec_iv.md", CH3_QUOTES),
        ("02-sources/02-Markdown/19_CHP-19Appendix.md", (APPENDIX_QUOTE,)),
    )
    for relative, quotes in source_checks:
        source_text = (ROOT / relative).read_text(encoding="utf-8-sig")
        for quote in quotes:
            assert normalized(quote) in normalized(source_text), f"source quote changed: {relative}: {quote[:80]!r}"

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    relation_candidates = [
        row for row in direct
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    assert {row["statement_id"] for row in relation_candidates} == set(RELATION_IDS)
    assert {row["statement_id"] for row in direct} == {*RELATION_IDS, "st-chp19-p386-appendix-archive-locator"}

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    old_phrase = (
        "The index slice and the body archive candidate therefore identify the same archival file/dossier "
        "and remain in one pending new archive group."
    )
    new_phrase = (
        "The index slice and the body archive candidate share the same printed archival citation locator "
        "and remain in one new archive identity group; the physical archival level and constituent records "
        "are not independently verified."
    )
    note_1532 = planned_by_id["cand-1532"]["resolution_note"]
    assert note_1532.count(old_phrase) == 1, "expected S3 file/dossier phrase is missing or ambiguous"
    planned_by_id["cand-1532"]["resolution_note"] = note_1532.replace(old_phrase, new_phrase, 1)
    for cid in MEMBERS:
        note = planned_by_id[cid]["resolution_note"]
        if IDENTITY_SCOPE.strip() not in note:
            note += IDENTITY_SCOPE
        note += f" S4 registration: mapped {GROUP} to {KU_ID}."
        planned_by_id[cid]["resolution_note"] = note
        planned_by_id[cid]["ku_id"] = KU_ID

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = card_text()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated archive card frontmatter is invalid"
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    next_process = process_sync.refresh_process_type_table(process_text, stats)
    assert f"<a id=\"{PROCESS_ANCHOR}\"></a>" not in next_process
    process_append = (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        f"### S4 archive：Jesuit Archives N. 865-13 跨章身份组登记（{DATE}）\n\n"
        f"- `{GROUP}` 含 `cand-1532`（M.csv#69，pp.386–387）与 `cand-5338`；登记为[{NAME_ZH}](../../../{CARD_REL})（`{KU_ID}`）。"
        "依据为第3章 p.88 注1–3与第19章附录1 p.386：三条脚注引用同一编号，注2、注3与附录题注交叉对应。\n"
        "- 本卡只把对象范围界定为哈斯克尔所载的档案引用定位号及其描述；不将其表述成已核实的实体卷宗、档案层级或已逐件查阅的原件。"
        "候选 `cand-11509` 是祭坛画作品类型，仍保持独立 S3 待决。\n"
        f"- 三条直接关系候选（{', '.join(RELATION_IDS)}）继续留待 S6；本批未登记正式关系或 S5 enrichment。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    next_process = next_process.rstrip() + process_append + "\n"

    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; "
            f"direct_statements={len(direct)}; relation_candidates_pending={len(relation_candidates)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; card_frontmatter=valid"
        )
        return 0

    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; "
        f"direct_statements={len(direct)}; relation_candidates_pending={len(relation_candidates)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
