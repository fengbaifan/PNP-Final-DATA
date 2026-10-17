from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_three_crosschapter_person_endpoints_20261017 as prior  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = "S4-full-book-2026-10-17"
ANCHOR = "s3-s4-osservatore-veneto-periodical-20261017"
CARD_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."
GROUP = "archive-group-osservatore-veneto-periodical"
KU = "units/archives/osservatore-veneto-periodical"
CANDIDATE = "cand-1791"
STATEMENT = "st-chp10-p323-gozzi-edits-osservatore-along-spectator-lines"

SOURCES = [
    {
        "location": "第10章，印刷页323，Markdown L190",
        "summary": "Haskell称Gasparo Gozzi编辑《Osservatore Veneto》，并按英国期刊The Spectator的路数编写。",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "source_span": "Markdown line 190; print p. 323",
        "quote": "the Osservatore Veneto which he edited on the lines of English journals such as The Spectator",
    },
    {
        "location": "第10章注2，印刷页324，Markdown L326",
        "summary": "Haskell注释引用《Osservatore Veneto》1761年2月14日一期作为Gozzi关于Longhi言论的出处；该期未在本项目中独立查阅。",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "source_span": "Markdown line 326; note 2 on print p. 324",
        "quote": "Osservatore Veneto, 14 Febbraio 1761.",
    },
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def keep_bom_bytes(path: Path, text: str) -> bytes:
    old = path.read_bytes() if path.exists() else b""
    bom = b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
    return bom + text.encode("utf-8")


def original_quote(source: dict) -> str:
    p = ROOT / source["source_file"]
    lines = p.read_text(encoding="utf-8-sig").splitlines()
    line = lines[int(source["source_span"].split("line ")[1].split(";")[0]) - 1]
    assert source["quote"] in line, f"quote missing: {source['source_file']} {source['source_span']}"
    return source["quote"]


def make_card() -> str:
    sources = []
    for source in SOURCES:
        line_num = source["source_span"].split("line ")[1].split(";")[0]
        sources.append(
            {
                "citation": BOOK_CITATION,
                "location": source["location"],
                "sentence_summary": source["summary"],
                "original_quotes": [{"source_span": f"Markdown line {line_num}", "text": original_quote(source)}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": source["source_file"],
                    "source_span": source["source_span"],
                },
            }
        )
    sources.append(
        {
            "citation": INDEX_CITATION,
            "location": "全书索引 O.csv#26",
            "sentence_summary": "索引词头为“Osservatore Veneto”，定位第10章p.323。",
            "original_quotes": [{"source_span": "O.csv#26; index row 28; p. 323", "text": "Osservatore Veneto"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/O.csv",
                "source_span": "O.csv#26; index row 28; p. 323",
            },
        }
    )
    frontmatter = yaml.safe_dump(
        {
            "title": "《Osservatore Veneto》期刊（Osservatore Veneto periodical）",
            "name_en": "Osservatore Veneto periodical",
            "type": "archive",
            "evidence_status": "source_backed",
            "sources": sources,
            "created": DATE,
            "updated": DATE,
            "process_ref": CARD_REF,
        },
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )
    return (
        f"---\n{frontmatter}---\n\n## 内容\n\n### 描述\n\n"
        "**中文：** 本卡记录Haskell所称由Gasparo Gozzi编辑的《Osservatore Veneto》期刊题名。第10章p.323将该刊与The Spectator相类比；p.324注2引用1761年2月14日一期，作为Gozzi评论Pietro Longhi的出处。卡片表示题名层级的期刊对象，不代表已查阅该期原件，也不据引文另建期号对象。中文说明保留刊名原文。\n\n"
        "**English:** This card records the periodical title *Osservatore Veneto* as named by Haskell and described as edited by Gasparo Gozzi. Chapter 10 p. 323 compares it with English journals such as *The Spectator*; note 2 on p. 324 cites an issue dated 14 February 1761 for Gozzi’s remarks on Pietro Longhi. The card represents the periodical at title level. It does not claim that the cited issue was consulted and does not create a separate issue object from the citation alone.\n\n"
        "## 关系与证据\n\n### 身份与外部链接\n\n"
        f"- S3 archive身份组：候选 `{CANDIDATE}`；查看 [alignment.csv](../../tables/alignment.csv) 与[本批过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。未采用外部权威标识。\n\n"
        "### 关系记录\n\n当前没有登记在 `relations.csv` 的正式关系。以下 S2 关系候选仍待 S6 审查，不因本次身份登记而视为已确认：\n\n"
        f"- [`{STATEMENT}`](../../tables/book-statements.jsonl)：Gozzi编辑期刊的陈述，待S6逐条审查。\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Adjudicate and register the Osservatore Veneto periodical title.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    align_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by = {r["candidate_id"]: r for r in candidates}
    planned = [dict(r) for r in alignments]
    planned_by = {r["candidate_id"]: r for r in planned if r.get("candidate_id") and not r.get("external_source")}
    manifest_by = {r["ku_id"]: r for r in manifest}
    statements = {
        r["statement_id"]: r
        for r in (json.loads(line) for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip())
    }
    accepted_lines = read_text(ACCEPTED_PATH).splitlines()
    c = candidate_by[CANDIDATE]
    a = planned_by[CANDIDATE]
    assert c["suggested_type"] == "archive"
    assert c["index_entry_id"] == "O.csv#26"
    assert a["decision"] == "undecided" and not a.get("ku_id")
    assert KU not in manifest_by and not (ROOT / f"04-knowledge/{KU}.md").exists()
    assert f"- 04-knowledge/{KU}.md" not in accepted_lines
    assert not any(r.get("name_en", "").casefold() == "osservatore veneto periodical" for r in manifest if r["type"] == "archive")
    assert b"Osservatore Veneto" in (ROOT / "02-sources/03-Index/03-2-Index-CSV/O.csv").read_bytes()
    for source in SOURCES:
        original_quote(source)
    assert STATEMENT in statements
    assert statements[STATEMENT].get("qualifiers", {}).get("relation_candidate") is True
    assert CANDIDATE in (statements[STATEMENT].get("subject_candidate_id"), statements[STATEMENT].get("object_candidate_id"))

    a["decision"] = "new"
    a["ku_id"] = KU
    a["process_ref"] = PROCESS_REF
    a["resolution_note"] += (
        f" S3 archive review ({DATE}): prior edition-level uncertainty is scoped to the cited issue, not the periodical title. "
        "Chapter 10 p.323 names Osservatore Veneto as a periodical edited by Gozzi; p.324 note 2 cites its 14 February 1761 issue. "
        f"Current decision: new title-level archive group={GROUP}, mapped to {KU}; the issue was not independently consulted and is not a separate KU."
    )
    c["detail"] = (
        f"S3 archive review ({DATE}): new title-level periodical group {GROUP}. The cited 14 February 1761 issue is retained as a bibliographic locator, "
        "not as an independently verified issue object."
    )
    cards = {ROOT / f"04-knowledge/{KU}.md": make_card()}
    planned_manifest = [dict(r) for r in manifest]
    planned_manifest.append(
        {
            "ku_id": KU,
            "type": "archive",
            "canonical_name": "《Osservatore Veneto》期刊（Osservatore Veneto periodical）",
            "name_en": "Osservatore Veneto periodical",
            "source_task": TASK,
            "card_path": f"04-knowledge/{KU}.md",
        }
    )
    planned_manifest.sort(key=lambda r: r["ku_id"])
    planned_accepted = prior.insert_accepted(accepted_lines, f"04-knowledge/{KU}.md")
    before_stats = sync.summarize_by_type(candidate_by.values(), alignments)
    _, before_totals = sync.build_type_table(before_stats)
    stats = sync.summarize_by_type(candidate_by.values(), planned)
    _, totals = sync.build_type_table(stats)
    assert len(planned_manifest) == len(manifest) + 1
    assert stats["archive"]["new_candidates"] == before_stats["archive"]["new_candidates"] + 1
    assert stats["archive"]["undecided"] == before_stats["archive"]["undecided"] - 1
    assert totals["registered_groups"] == before_totals["registered_groups"] + 1
    assert totals["pending_groups"] == before_totals["pending_groups"]

    process_text = read_text(PROCESS_PATH)
    anchor = f'<a id="{ANCHOR}"></a>'
    assert anchor not in process_text
    process_text += (
        "\n\n" + anchor + "\n\n"
        "### S3 archive→S4：Osservatore Veneto 期刊题名裁决与登记（2026-10-17）\n\n"
        "`cand-1791`（O.csv#26）由 `undecided` 改为 `new`，进入一个题名层级 archive 组。第10章p.323明确称《Osservatore Veneto》为Gasparo Gozzi编辑的期刊；"
        "p.324注2给出1761年2月14日期号，作为Gozzi评论Longhi的出处。原待证理由所指的版次/期号缺口不妨碍确定期刊题名本身；卡片不声称已查阅该期，也不另建期号KU。"
        "S2直接关系候选 `st-chp10-p323-gozzi-edits-osservatore-along-spectator-lines` 留待S6，未新增正式关系。\n\n"
        f"[archive卡片](../../../04-knowledge/{KU}.md)；对齐决定保留在alignment.csv，候选详情记录题名层级与期号边界。\n"
    )
    result_text = sync.update_result(read_text(RESULT_PATH), stats, totals, len(planned_manifest))
    result_text += (
        "\n\n### S3 archive→S4：Osservatore Veneto 期刊题名裁决与登记（2026-10-17）\n\n"
        f"`cand-1791`（O.csv#26）由待证改为题名层级 archive 新组，登记为[《Osservatore Veneto》期刊卡](../{KU}.md)。"
        "正文和注释支持期刊题名及1761年2月14日的引文定位；该期未独立查阅，不另建期号对象。1条直接关系候选留待S6。\n"
    )

    if args.dry_run:
        print("DRY-RUN OK: cand-1791 undecided->new archive title group; one KU; one S6 relation candidate")
        print(
            f"manifest: {len(manifest):,}->{len(planned_manifest):,}; new candidates: {before_totals['new_candidates']:,}->{totals['new_candidates']:,}; "
            f"undecided: {before_totals['undecided']:,}->{totals['undecided']:,}; "
            f"registered groups: {before_totals['registered_groups']:,}->{totals['registered_groups']:,}; "
            f"pending groups: {before_totals['pending_groups']:,}->{totals['pending_groups']:,}"
        )
        return

    for path, card in cards.items():
        path.write_bytes(card.encode("utf-8"))
    sync.write_csv(ALIGNMENT_PATH, align_fields, planned)
    sync.write_csv(ENTITY_PATH, candidate_fields, candidates)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_bytes(keep_bom_bytes(ACCEPTED_PATH, "\n".join(planned_accepted) + "\n"))
    PROCESS_PATH.write_bytes(keep_bom_bytes(PROCESS_PATH, process_text))
    RESULT_PATH.write_bytes(keep_bom_bytes(RESULT_PATH, result_text))
    print(f"APPLIED: {CANDIDATE} -> {KU}; S3 new title group; registered groups={totals['registered_groups']:,}")


if __name__ == "__main__":
    main()
