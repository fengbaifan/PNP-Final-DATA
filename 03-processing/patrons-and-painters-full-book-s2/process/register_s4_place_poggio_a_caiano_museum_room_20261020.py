from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
TABLES = ROOT / "04-knowledge" / "tables"
sys.path.insert(0, str(PROCESS_DIR))

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as result_sync
import register_s4_work_second_scuola_scheme_20261020 as s4_helpers

PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
AGENTS_PATH = ROOT / "AGENTS.md"

CANDIDATE = "cand-7963"
GROUP = "sg3-place-cand-7963"
KU_ID = "units/places/poggio-a-caiano-museum-room"
CARD_REL = "04-knowledge/units/places/poggio-a-caiano-museum-room.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "波焦阿卡亚诺费迪南德画廊中的博物馆房间"
NAME_EN = "Museum room in Ferdinand’s gallery at Poggio a Caiano"
DATE = "2026-10-20"
SOURCE_CH8 = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE_APP = "02-sources/02-Markdown/19_CHP-19Appendix.md"
CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)
PROCESS_ANCHOR = "s4-place-poggio-a-caiano-museum-room-direct-endpoint-20261020"
HEADING = "### S4 place：波焦阿卡亚诺费迪南德画廊中的博物馆房间（2026-10-20）"
DIRECT_IDS = {
    "st-chp8-p235-poggio-visit-postponed",
    "st-chp19-p390-ricci-museum-room-plan",
    "st-chp19-p390-ferdinand-defers-room",
    "st-chp8-p235-ferdinand-postpones-poggio-scheme",
}
QUOTE_SNIPPETS = {
    SOURCE_CH8: (
        "to paint a room in Ferdinand’s gallery of Venetian pictures at Poggio a Caiano",
        "Ferdinand’s reply a week later was somewhat discouraging: ill-health was causing him to postpone the projected scheme.",
    ),
    SOURCE_APP: (
        "poter dipingere la stanza del museo",
        "non è ancora in grado da potersi lavorare",
        "a suo tempo d.a stanza è destinata",
    ),
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def make_card() -> str:
    source_records = [
        {
            "citation": f"{CITATION} 第8章，印刷页235。",
            "location": "第8章，印刷页235；来源转录第298行。",
            "sentence_summary": "Haskell称 Ricci 提及赴佛罗伦萨为 Ferdinand 在 Poggio a Caiano 的威尼斯画作画廊绘制一间房间，并称 Ferdinand 因病推迟计划。",
            "original_quotes": [
                {
                    "source_span": "line 298; print p. 235",
                    "text": "to paint a room in Ferdinand’s gallery of Venetian pictures at Poggio a Caiano",
                },
                {
                    "source_span": "line 298; print p. 235",
                    "text": "Ferdinand’s reply a week later was somewhat discouraging: ill-health was causing him to postpone the projected scheme.",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_CH8,
                "source_span": "line 298; print p. 235",
            },
        },
        {
            "citation": f"{CITATION} 附录，印刷页390。",
            "location": "附录，印刷页390；来源转录第95、98–99行。",
            "sentence_summary": "Haskell转录 Ricci 1706年5月1日致 Ferdinand 的信及 Ferdinand 5月8日的回复；房间当时尚不能施工，但仍拟由 Ricci 绘制。原档案信件在本项目中未直接查阅。",
            "original_quotes": [
                {
                    "source_span": "letter of 1 May 1706; line 95; print p. 390",
                    "text": "poter dipingere la stanza del museo",
                },
                {
                    "source_span": "letter of 8 May 1706; lines 98–99; print p. 390",
                    "text": "non è ancora in grado da potersi lavorare; a suo tempo d.a stanza è destinata p. esser dipinta da lei",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_APP,
                "source_span": "lines 95, 98–99; print p. 390",
            },
        },
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "place",
        "evidence_status": "source_backed",
        "sources": source_records,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔所述 Poggio a Caiano 的一间博物馆房间：第8章称它位于 Ferdinand 的威尼斯画作画廊；[Sebastiano Ricci](../persons/sebastiano-ricci.md) 曾提及赴佛罗伦萨绘制，[Grand Prince Ferdinand de’ Medici](../persons/ferdinand-grand-prince-tuscany.md) 随后因病推迟计划（[第8章 p.235](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)）。附录转录的1706年5月1日信写 Ricci 希望绘制 Ferdinand 命其绘制的博物馆房间；5月8日回复称房间尚未准备好施工，但仍拟在适当时候由 Ricci 绘制（[附录 p.390](../../../02-sources/02-Markdown/19_CHP-19Appendix.md)）。此处“博物馆房间”按书内所述的建筑内部空间登记为 place。信件内容依据 Haskell 的转录，未直接查阅所引档案原件。来源没有证明房间最终完成、具体建筑平面或现存实体身份。

**English:** This unit records a museum room at Poggio a Caiano as described by Haskell. Chapter 8 places it in Ferdinand’s gallery of Venetian pictures; [Sebastiano Ricci](../persons/sebastiano-ricci.md) had mentioned a visit to Florence to paint it, after which [Grand Prince Ferdinand de’ Medici](../persons/ferdinand-grand-prince-tuscany.md) postponed the scheme because of ill health ([chapter 8, p. 235](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)). The appendix transcribes Ricci’s letter of 1 May 1706, in which he hoped to paint the museum room Ferdinand had commissioned, and Ferdinand’s reply of 8 May, which says the room was not yet ready for work but remained intended for Ricci at the appropriate time ([appendix, p. 390](../../../02-sources/02-Markdown/19_CHP-19Appendix.md)). The room is registered as a place because it is an interior space in the source account. The account does not establish completion, architectural details, or a present-day physical identity. The letters are known here through Haskell’s transcription; the cited archival originals were not directly consulted.

### 身份边界

本组限于第8章 p.235 与附录 p.390 所述、拟由 Ricci 绘制的房间。它不与候选 cand-8062 所述 Ferdinand 后来收藏小幅画作的 special room 自动合并。Farsetti 后来提及 Poggio 的威尼斯画作房间有彩绘天顶；该转述不证明 Ricci 的计划已经完成，也不能据此将该天顶等同于已毁的 Allegory of the Arts。Poggio a Caiano 别墅本身与房间保持为不同地点粒度。

### 本书相关内容

本组涉及 Sebastiano Ricci 与 Grand Prince Ferdinand 的 S2 关系候选，但登记地点本身不表示候选关系已经成立。4条候选的逐条裁决及其 statement ID 见[过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-place-poggio-a-caiano-museum-room-direct-endpoint-20261020)。

## 关系与证据

### 身份与外部链接

本组是来源所述房间的描述性地点登记；目前没有同粒度且已核验的外部权威身份记录或外部链接。

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

本次未新增正式关系；S2 中与本地点相连的4条候选仍待 S6 逐条裁决，见上方过程记录链接。
"""


def write_csv_preserving_bom(path: Path, fields, rows) -> None:
    had_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    result_sync.write_csv(path, fields, rows)
    if not had_bom and path.read_bytes().startswith(b"\xef\xbb\xbf"):
        path.write_bytes(path.read_bytes()[3:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Poggio a Caiano museum room endpoint in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    assert CANDIDATE in candidate_by_id
    candidate = candidate_by_id[CANDIDATE]
    assert candidate.get("suggested_type") == "place"
    assert candidate.get("candidate_source_ref") == "chp-8:08_CHP-8_sec_ii:l291-301#L298"

    decisions = [
        row for row in alignments
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    ]
    assert len(decisions) == 1
    target = decisions[0]
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert result_sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and result_sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row.get("candidate_id") for row in group_rows] == [CANDIDATE]
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "place"
        and (row.get("name_en", "").casefold() == NAME_EN.casefold()
             or row.get("canonical_name", "").casefold() == NAME_ZH.casefold())
        for row in manifest
    ), "same-title place already exists in the manifest"

    source_texts = {
        rel: normalize((ROOT / rel).read_text(encoding="utf-8-sig"))
        for rel in QUOTE_SNIPPETS
    }
    for rel, snippets in QUOTE_SNIPPETS.items():
        for snippet in snippets:
            assert normalize(snippet) in source_texts[rel], (rel, snippet)

    statements = result_sync.load_statements()
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE
        or row.get("object_candidate_id") == CANDIDATE
    ]
    assert {row["statement_id"] for row in direct} == DIRECT_IDS
    assert all(row.get("qualifiers", {}).get("relation_candidate") is True for row in direct)
    assert all(row.get("origin") == "book" for row in direct)

    planned_alignment = [dict(row) for row in alignments]
    planned_target = next(
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    planned_target["ku_id"] = KU_ID
    planned_target["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}"
    planned_target["resolution_note"] = (
        (planned_target.get("resolution_note") or "")
        + f" S4 registration ({DATE}): mapped {GROUP} to {KU_ID}; a source-described interior museum room at Poggio a Caiano. "
        "The prospective Ricci project is not treated as completed, and the room is not conflated with later galleries."
    )

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "place",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    stats = result_sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]

    before_queue = s4_helpers.compute_direct_queue(candidate_by_id, alignments, statements)
    after_queue = s4_helpers.compute_direct_queue(candidate_by_id, planned_alignment, statements)
    assert before_queue["groups"] == after_queue["groups"] + 1
    assert before_queue["members"] == after_queue["members"] + 1
    assert before_queue["endpoint_candidates"] == after_queue["endpoint_candidates"] + 1

    for statement in direct:
        endpoints = {
            statement.get("subject_candidate_id"),
            statement.get("object_candidate_id"),
        } - {None, ""}
        assert CANDIDATE in endpoints and len(endpoints) == 2
        for endpoint_id in endpoints - {CANDIDATE}:
            endpoint_candidate = candidate_by_id[endpoint_id]
            endpoint_rows = [
                row for row in alignments
                if row.get("candidate_id") == endpoint_id and not row.get("external_source")
            ]
            assert len(endpoint_rows) == 1
            endpoint_alignment = endpoint_rows[0]
            assert endpoint_alignment.get("decision") in {"same", "new"}
            assert endpoint_alignment.get("ku_id")
            endpoint_manifest = next(
                row for row in manifest if row.get("ku_id") == endpoint_alignment["ku_id"]
            )
            assert endpoint_manifest.get("type") == endpoint_candidate.get("suggested_type")

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    assert PROCESS_ANCHOR not in process_text and HEADING not in process_text
    assert HEADING not in result_text
    process_text = s4_helpers.refresh_knowledge_table(process_text, stats)
    process_entry = (
        f"\n\n{HEADING}\n\n"
        f"{CANDIDATE} 沿用既有 S3 new 身份组 {GROUP}，登记至"
        f"[知识卡](../../../{CARD_REL})。第8章 p.235 将房间定位在 Ferdinand 的威尼斯画作画廊，"
        "并记 Ricci 拟赴佛罗伦萨绘制、Ferdinand 因病推迟；附录 p.390 所录 1706年5月1日与8日信件分别记 Ricci 的绘制计划"
        "和 Ferdinand 关于房间尚未准备好、以后仍拟由 Ricci 绘制的回复。原始档案信件未直接查阅。"
        "身份范围限于该书内描述的室内空间，不推定施工完成，不与后来的 special room 或 Farsetti 所述天顶自动合并。"
        f"4条直接 S2 关系候选（{', '.join(sorted(DIRECT_IDS))}）的另一端均已有类型相符的 KU，仍留待 S6；"
        "本批未新增 S2 statements/mentions、S5 字段或 formal 关系。"
        f"S4登记后为 {result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['new_groups'])} 组、"
        f"{result_sync.fmt(totals['registered_members'])}/{result_sync.fmt(totals['new_candidates'])} 条映射；"
        f"直接端点队列由 {before_queue['groups']:,} 组／{before_queue['members']:,} 成员降至 "
        f"{after_queue['groups']:,} 组／{after_queue['members']:,} 成员。"
    )
    process_text = process_text.rstrip() + process_entry + "\n"

    result_text = result_sync.update_result(
        result_text, stats, totals, len(planned_manifest)
    )
    result_entry = (
        f"\n\n{HEADING}\n\n"
        f"{CANDIDATE} 沿用既有 S3 new 组 {GROUP} 登记为"
        f"[地点卡](../units/places/poggio-a-caiano-museum-room.md)。第8章 p.235 与附录 p.390 所录 1706年书信"
        "支持其为 Ferdinand 在 Poggio a Caiano 的威尼斯画作画廊中的博物馆房间，且 Ricci 的绘制计划当时被推迟；"
        "原始档案信件未直接查阅。本卡不声称房间最终完成或与后来的房间、天顶装饰为同一对象。"
        f"4条直接 S2 关系候选（{', '.join(sorted(DIRECT_IDS))}）均有类型匹配的另一端 KU，仍待 S6 逐条裁决；"
        f"登记后 S4 已登记{result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['new_groups'])}组、"
        f"{result_sync.fmt(totals['registered_members'])}/{result_sync.fmt(totals['new_candidates'])}条映射，"
        f"待登记{result_sync.fmt(totals['pending_groups'])}组／{result_sync.fmt(totals['pending_members'])}条映射。"
    )
    result_text = result_text.rstrip() + result_entry + "\n"

    relations = result_sync.read_csv(TABLES / "relations.csv")[1]
    enrichment = [
        json.loads(line)
        for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    agents_text = s4_helpers.refresh_agents(
        AGENTS_PATH.read_text(encoding="utf-8-sig"),
        totals, after_queue, statements, relations, enrichment,
    )

    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    accepted_text = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 place dry-run passed: {CANDIDATE} -> {KU_ID}; group members={len(group_rows)}")
        print(f"source snippets checked={sum(map(len, QUOTE_SNIPPETS.values()))}; direct statements={len(direct)}")
        print("counterpart KUs are registered and type-matched; no formal relation or S5 field is created")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted path unique")
        print(
            f"registered={totals['registered_groups']:,}/{totals['new_groups']:,} groups, "
            f"{totals['registered_members']:,}/{totals['new_candidates']:,} mappings; "
            f"pending={totals['pending_groups']:,}/{totals['pending_members']:,}"
        )
        print(
            f"direct queue={before_queue['groups']:,}/{before_queue['members']:,} -> "
            f"{after_queue['groups']:,}/{after_queue['members']:,}"
        )
        print("alignment, result table, process table, and AGENTS snapshot refreshed in memory only")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8", newline="\n")
    write_csv_preserving_bom(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv_preserving_bom(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(accepted_text, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8", newline="\n")
    AGENTS_PATH.write_text(agents_text, encoding="utf-8", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={totals['registered_groups']:,}/{totals['registered_members']:,}; "
        f"pending={totals['pending_groups']:,}/{totals['pending_members']:,}; "
        f"direct={before_queue['groups']:,}->{after_queue['groups']:,} groups"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
