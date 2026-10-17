from __future__ import annotations

import argparse
import csv
import difflib
import io
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
CARD_REL = "04-knowledge/units/archives/brugnoli-albani-domenichino-frescoes-bassano-sutri-1957.md"
CARD_PATH = ROOT / CARD_REL
KU_ID = "units/archives/brugnoli-albani-domenichino-frescoes-bassano-sutri-1957"
GROUP = "archive-group-brugnoli-albani-domenichino-bassano-1957"
CIDS = ("cand-4329", "cand-11270")
DATE = "2026-10-17"
ANCHOR = "s3-s4-brugnoli-albani-domenichino-article-20261017"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CHP2_FILE = "02-sources/02-Markdown/02_CHP-2_sec_i.md"
CHP21_FILE = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
QUOTE_CHP2 = (
    "For Giustiniani see the inventory of his pictures published by Salerno, i960; and also the "
    "articles by Paolo Portoghesi, M. V. Brugnoli, Italo Faldi and I. Toesca in 1957."
)
QUOTE_BIB = "‘Gli affreschi dell’Albani e del Domenichino nel Palazzo di Bassano di Sutri’"
RELATION_IDS = ("st-chp2-seci-l95-106-citation-brugnoli-frescoes",)
NAME_ZH = "布鲁诺利《苏特里巴萨诺宫阿尔巴尼与多梅尼基诺壁画》"
NAME_EN = "M. V. Brugnoli, ‘Gli affreschi dell’Albani e del Domenichino nel Palazzo di Bassano di Sutri’"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    old = path.read_bytes() if path.exists() else b""
    bom = b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
    path.write_bytes(bom + text.encode("utf-8"))


def render_csv(fieldnames, rows) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def show_diff(path: str, old: str, new: str) -> None:
    diff = difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f"a/{path}", tofile=f"b/{path}",
    )
    print("".join(diff), end="")


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第2章；印刷页29；注5；Markdown L104",
            "sentence_summary": (
                "Haskell 的注释提到 Brugnoli 等作者的1957年论文；该处为书内引文指针，"
                "没有给出论文完整题名，也没有验证所引论文的内容。"
            ),
            "original_quotes": [{"source_span": "L104; note 5, print p. 29", "text": QUOTE_CHP2}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHP2_FILE,
                "source_span": "L104; note 5, print p. 29",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第21章参考书目；印刷页417；Markdown L266–268",
            "sentence_summary": (
                "Haskell 的参考书目列出本文题名和 M. V. Brugnoli 责任者。S2 页图布局记录将 "
                "Bollettino d’Arte、1957年及255–277页判读为同一条目中两篇 Brugnoli 论文的共同刊载信息；"
                "本文仅据该书目记录识别，未独立查阅。"
            ),
            "original_quotes": [{"source_span": "L266–268; print p. 417", "text": QUOTE_BIB}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHP21_FILE,
                "source_span": "L266–268; print p. 417",
            },
        },
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "scholarly_article",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    chp2_link = f"[第2章 p.29 注5](../../../{CHP2_FILE}#L104)"
    bib_link = f"[第21章书目 p.417](../../../{CHP21_FILE}#L266)"
    body = f"""## 内容

### 描述

**中文：** 本卡登记 Haskell 第21章参考书目所列 M. V. Brugnoli 论文 *Gli affreschi dell’Albani e del Domenichino nel Palazzo di Bassano di Sutri*。中文题名为描述性工作译名。Haskell 第2章注释在 Giustiniani 讨论中提及 Brugnoli 等人的1957年论文；论文题名、刊物和页码范围依据 Haskell 书目及其页图布局记录。本文未独立查阅，卡片不转述论文内容。作者只按书目中的姓名缩写记录，未据此确认作者个人身份。{chp2_link}；{bib_link}

**English:** This card records M. V. Brugnoli’s article *Gli affreschi dell’Albani e del Domenichino nel Palazzo di Bassano di Sutri*, listed in Haskell’s Chapter 21 bibliography. The Chinese title is a descriptive working translation. Haskell’s Chapter 2 note mentions 1957 articles by Brugnoli and others in the context of Giustiniani; the article title, journal, and page span are based on Haskell’s bibliography and its recorded page-image layout. The article itself was not consulted, and no account of its contents is supplied. The author is recorded by the initials printed in the bibliography; no personal identity is inferred. {chp2_link}; {bib_link}

### 书目身份

- **题名：** *Gli affreschi dell’Albani e del Domenichino nel Palazzo di Bassano di Sutri*；中文为描述性工作译名。{bib_link}
- **责任者：** M. V. Brugnoli，依 Haskell 书目照录；全名未据此确认。{bib_link}
- **刊载信息：** *Bollettino d’Arte*，1957年，pp. 255–277。Haskell 的同一书目项还列 Brugnoli 的另一篇题名不同的文章；S2 页图布局记录将刊名、年份与页码范围归于两篇文章共同刊载信息。本卡只登记本题名对应的一篇。{bib_link}
- **阅读范围：** 仅核对 Haskell 第2章引注和第21章书目；Brugnoli 论文原文及其所引内容未独立查阅。{chp2_link}；{bib_link}

### 身份边界

本卡与同一书目项中的 Brugnoli 另一篇论文 *Il soggiorno a Roma di Bernardo Castello e le sue pitture nel Palazzo di Bassano di Sutri* 分开登记；作者相同、年份相同及共享页码不表示两篇文章是同一文献。`cand-4327` 的作者人物身份仍为 S3 `undecided`，本卡不创建或链接人物 KU。

## 关系与证据

### 关系记录

本卡没有新增正式关系。以下1条书内引文候选仍待S6审查：

{chr(10).join(f'- `{sid}`' for sid in RELATION_IDS)}
"""
    return f"---\n{fm}---\n\n{body}"


def add_accepted_path(text: str) -> str:
    lines = text.splitlines()
    target = f"- {CARD_REL}"
    assert target not in lines
    units_end = next((i for i, line in enumerate(lines) if line.startswith("claims:")), len(lines))
    unit_lines = [line for line in lines[:units_end] if line.startswith("- 04-knowledge/units/")]
    assert CARD_REL not in {line[2:] for line in unit_lines}
    insert_at = next(
        (i for i, line in enumerate(lines[:units_end])
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        units_end,
    )
    lines.insert(insert_at, target)
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter Brugnoli article identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert all(cid in candidate_by_id and cid in alignment_by_id for cid in CIDS)
    for cid in CIDS:
        assert candidate_by_id[cid]["suggested_type"] == "archive"
        assert alignment_by_id[cid]["decision"] == "new"
        assert sync.get_group(alignment_by_id[cid].get("resolution_note", "")) == GROUP
    group_members = {
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(CIDS), group_members
    assert alignment_by_id["cand-4328"]["decision"] == "new"
    assert sync.get_group(alignment_by_id["cand-4328"].get("resolution_note", "")) != GROUP
    assert alignment_by_id["cand-4327"]["decision"] == "undecided"

    statements = sync.load_statements()
    actual_relations = {
        row["statement_id"] for row in statements
        if set(CIDS).intersection((row.get("subject_candidate_id"), row.get("object_candidate_id")))
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert actual_relations == set(RELATION_IDS), actual_relations
    chp2 = " ".join((ROOT / CHP2_FILE).read_text(encoding="utf-8-sig").split())
    chp21 = " ".join((ROOT / CHP21_FILE).read_text(encoding="utf-8-sig").split())
    assert " ".join(QUOTE_CHP2.split()) in chp2
    assert "Gli affreschi dell’Albani e del Domenichino nel Palazzo di" in chp21

    registered_rows = [row for row in manifest if row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL]
    name_rows = [
        row for row in manifest
        if row.get("type") == "archive" and (row.get("name_en") or "").casefold() == NAME_EN.casefold()
    ]
    accepted_text = read_text(ACCEPTED_PATH)
    accepted_paths = {
        line[2:] for line in accepted_text.splitlines()
        if line.startswith("- 04-knowledge/units/")
    }
    registered = (
        len(registered_rows) == 1 and registered_rows[0].get("ku_id") == KU_ID
        and all(alignment_by_id[cid].get("ku_id") == KU_ID for cid in CIDS)
        and CARD_REL in accepted_paths and CARD_PATH.exists()
    )
    assert len(registered_rows) <= 1 and len(name_rows) <= 1
    if registered:
        assert len(name_rows) == 1 and name_rows[0].get("ku_id") == KU_ID
        assert all(f"S4 registration: mapped {GROUP} to {KU_ID}." in alignment_by_id[cid].get("resolution_note", "") for cid in CIDS)
        print(f"ALREADY REGISTERED: {','.join(CIDS)} -> {KU_ID}; {len(actual_relations)} relation candidate remains for S6.")
        return 0
    assert not registered_rows and not name_rows
    assert not any(alignment_by_id[cid].get("ku_id") for cid in CIDS)
    assert CARD_REL not in accepted_paths and not CARD_PATH.exists()

    existing_process = read_text(PROCESS_PATH)
    existing_result = read_text(RESULT_PATH)
    assert ANCHOR not in existing_process
    planned_alignments = [dict(row) for row in alignments]
    planned_alignment_by_id = {row["candidate_id"]: row for row in planned_alignments if row.get("candidate_id")}
    for cid in CIDS:
        target = planned_alignment_by_id[cid]
        target["resolution_note"] += (
            " S3 cross-chapter adjudication: this candidate and the paired bibliography/citation candidate "
            "identify the second Brugnoli article listed at Haskell, p. 417; the first, differently titled "
            "Brugnoli article remains a separate identity. The cited article was not independently read."
        )
        target["ku_id"] = KU_ID
        target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(values[key] for values in stats.values()) for key in next(iter(stats.values()))}
    new_result = sync.update_result(existing_result, stats, totals, len(planned_manifest)).rstrip()
    new_result += (
        "\n\n### archive：Brugnoli 第二篇论文跨章身份组 S3/S4 登记（2026-10-17）\n\n"
        "`cand-4329`（第2章注5）与`cand-11270`（第21章书目）作为同一篇 Brugnoli 论文跨章映射至"
        "[文献卡](../units/archives/brugnoli-albani-domenichino-frescoes-bassano-sutri-1957.md)。"
        "书目中的另一篇 Brugnoli 论文题名不同，仍为独立对象；两篇文章未被独立查阅。"
        "`cand-4327`作者人物身份保留 `undecided`；1条书内引文关系候选留待S6，没有新增正式关系。\n\n"
        f"全书S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    new_process = existing_process.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S3/S4 archive：Brugnoli 第二篇论文跨章身份组登记（2026-10-17）\n\n"
        "`cand-4329`（第2章 p.29 注5）与`cand-11270`（第21章 p.417 书目）构成同一 archive 身份组 `archive-group-brugnoli-albani-domenichino-bassano-1957`。第2章注释提及 Brugnoli 等人的1957年论文；第21章书目提供第二篇文章的完整题名，S2 页图布局记录将 *Bollettino d’Arte*、1957年及 pp.255–277 归为同一条目中两篇文章的共同刊载信息。卡片只登记书目身份，不表示原文或文章内容已经查阅。\n\n"
        "该书目项还列有题名不同的 Brugnoli 论文 *Il soggiorno a Roma di Bernardo Castello e le sue pitture nel Palazzo di Bassano di Sutri*，其候选 `cand-4328` 保持另一 S3 身份组。作者人物候选 `cand-4327` 因仅有缩写仍为 `undecided`。\n\n"
        f"S4将两条组成员映射至[Brugnoli论文卡](../../../{CARD_REL})。`st-chp2-seci-l95-106-citation-brugnoli-frescoes` 仍待S6；没有新增正式关系或外部事实断言。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    new_accepted = add_accepted_path(accepted_text)
    new_card = make_card()

    if args.dry_run:
        print(f"S3 group: {','.join(CIDS)} -> {GROUP} (archive; chp-2 + chp-21).")
        print(f"S4: add {KU_ID} ({CARD_REL}); cand-4328 remains separate, cand-4327 remains undecided.")
        print(f"Counts: registered groups={totals['registered_groups']}, members={totals['registered_members']}, "
              f"pending groups={totals['pending_groups']}, members={totals['pending_members']}, "
              f"KU={len(planned_manifest)}; {len(actual_relations)} relation candidate remains for S6.")
        print("Planned files: alignment.csv, ku-manifest.csv, accepted.yml, archive card, process/knowledge.md, result.")
        print("\n--- Reviewable diff ---")
        show_diff("04-knowledge/tables/alignment.csv", render_csv(alignment_fields, alignments), render_csv(alignment_fields, planned_alignments))
        show_diff("04-knowledge/tables/ku-manifest.csv", render_csv(manifest_fields, manifest), render_csv(manifest_fields, planned_manifest))
        show_diff("04-knowledge/accepted.yml", accepted_text, new_accepted)
        show_diff(CARD_REL, "", new_card)
        show_diff("03-processing/patrons-and-painters-full-book-s2/process/knowledge.md", existing_process, new_process)
        show_diff("04-knowledge/results/patrons-and-painters-full-book-s2.md", existing_result, new_result)
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_text(ACCEPTED_PATH, new_accepted)
    write_text(CARD_PATH, new_card)
    write_text(PROCESS_PATH, new_process)
    write_text(RESULT_PATH, new_result)
    print(f"APPLIED: {','.join(CIDS)} -> {KU_ID}; {len(actual_relations)} relation candidate remains pending S6.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
