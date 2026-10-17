from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import shutil
from io import StringIO
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge/tables"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
KNOWLEDGE = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge/results" / f"{TASK}.md"
DATE = "2026-10-16"

CANDIDATE = "cand-1489"
PRIOR_GROUP = "new-person:francesco-maggiotto-908b8d8efa"
KU_ID = "units/persons/francesco-maggiotto"
CARD_REL = "04-knowledge/units/persons/francesco-maggiotto.md"
FATHER_KU = "units/persons/domenico-fedeli-venice-painter"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
TRECCANI_URL = "https://www.treccani.it/enciclopedia/fedeli-francesco-detto-il-maggiotto_(Dizionario-Biografico)/"
ULAN_URL = "https://www.getty.edu/vow/ULANFullDisplay?find=500028440&nation=&page=1&role=&subjectid=500125012"
ULAN_ID = "500125012"
WIKIDATA_ID = "Q3080993"
WIKIDATA_URL = f"https://www.wikidata.org/wiki/{WIKIDATA_ID}"
BACKUP_SUFFIX = ".bak-s3-same-francesco-maggiotto-20261016"

BOOK_SOURCES = (
    {
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "location": "第10章 p.325；OCR L203–208",
        "span": "lines 203–208; print p. 325",
        "summary": "正文以全名 Francesco Maggiotto 记其为关注科学的画家，并称他发明电机、撰写相关论著；同段继续评价其风俗画。",
        "quotes": (
            ("line 206", "Francesco Maggiotto, was so far affected by advanced scientific ideas"),
            ("line 206", "he actually invented an electrical machine and wrote a treatise on the subject"),
        ),
    },
    {
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        "location": "第13章 p.340；OCR L79–82",
        "span": "lines 80–82; print p. 340",
        "summary": "正文以全名称 Francesco Maggiotto，并记 Maffeo Pinelli 与其交往密切及委托其绘制一组 Doge 肖像等作品。",
        "quotes": (
            ("line 80", "the painter with whom he was most in touch was a late and second-hand follower of Piazzetta, Francesco Maggiotto"),
            ("lines 80–81", "He painted for Pinelli a series of portraits of all the Doges"),
        ),
    },
    {
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "location": "第20章后记 pp.408–409；OCR L184–188",
        "span": "lines 184–188; print pp. 408–409",
        "summary": "后记以全名回顾 Francesco Maggiotto 为 Pinelli 绘制 Doge 肖像，称至少六幅后来重现；作品身份与现有卡所记录图版68a三幅肖像仍按各自作品候选边界处理。",
        "quotes": (
            ("line 184", "the Doges which were painted for him by Francesco Maggiotto"),
            ("line 184", "At least six of the little oval portraits on copper"),
        ),
    },
    {
        "source_file": "02-sources/02-Markdown/00_05_List_of_Plates.md",
        "location": "章前图版目录；印刷页 xvi；OCR L78–79；Plate 68a",
        "span": "lines 78–79; printed plate list p. xvi",
        "summary": "本书图版68a以 Francesco Maggiotto 署名三幅 Doges 肖像；现有人物卡已用该来源登记此人。",
        "quotes": (("line 158", "68 a Francesco Maggiotto: Three portraits of Doges"),),
    },
    {
        "source_file": "02-sources/03-Index/03-2-Index-CSV/M.csv",
        "location": "全书索引 M.csv#26；页码 325、340、408、409",
        "span": "M.csv#26",
        "summary": "索引以 Maggiotto, Francesco 汇集第10章、第13章与后记相关页码。",
        "quotes": (("M.csv#26", "Maggiotto, Francesco"),),
    },
)


def normalize(text: str) -> str:
    return " ".join(text.split())


def contains_candidate(value, candidate_id: str) -> bool:
    if isinstance(value, dict):
        return any(contains_candidate(item, candidate_id) for item in value.values())
    if isinstance(value, list):
        return any(contains_candidate(item, candidate_id) for item in value)
    return value == candidate_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-review the Francesco Maggiotto S3 candidate for reuse of an accepted person KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(CANDIDATES)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _, manifest = sync.read_csv(MANIFEST)
    candidate = next(row for row in candidates if row.get("candidate_id") == CANDIDATE)
    target = next(
        row for row in alignments
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    accepted_candidate = next(
        row for row in candidates
        if row.get("candidate_origin") == "accepted-ku"
        and row.get("candidate_source_ref") == CARD_REL
    )
    accepted_alignment = next(
        row for row in alignments
        if row.get("candidate_id") == accepted_candidate["candidate_id"]
        and not row.get("external_source")
    )
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Maggiotto, Francesco"
    assert candidate.get("index_entry_id") == "M.csv#26"
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert sync.get_group(target.get("resolution_note", "")) == PRIOR_GROUP
    prior_group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == PRIOR_GROUP
    ]
    assert [row["candidate_id"] for row in prior_group_rows] == [CANDIDATE]
    assert accepted_alignment.get("decision") == "same"
    assert accepted_alignment.get("ku_id") == KU_ID
    assert any(row.get("ku_id") == KU_ID and row.get("card_path") == CARD_REL for row in manifest)
    assert any(row.get("ku_id") == FATHER_KU for row in manifest)
    assert (ROOT / CARD_REL).exists()
    assert "Francesco Maggiotto" in (ROOT / CARD_REL).read_text(encoding="utf-8-sig")
    assert not any(
        row.get("candidate_id") == CANDIDATE and row.get("external_source")
        for row in alignments
    ), "external identity records already exist for candidate"

    _, index_rows = sync.read_csv(ROOT / "02-sources/03-Index/03-2-Index-CSV/M.csv")
    index_row = index_rows[int(candidate["index_entry_id"].split("#")[1])]
    assert index_row.get("Main Entry") == candidate["canonical_name"]
    assert index_row.get("Page Numbers") == "325, 340, 408, 409"
    for item in BOOK_SOURCES:
        normalized_source = normalize((ROOT / item["source_file"]).read_text(encoding="utf-8-sig"))
        for _, quote in item["quotes"]:
            assert normalize(quote) in normalized_source, (item["source_file"], quote)

    statements = [
        json.loads(line)
        for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    related = [row for row in statements if contains_candidate(row, CANDIDATE)]
    relation_count = sum(
        row.get("qualifiers", {}).get("relation_candidate") is True
        for row in related
    )
    assert len(related) == 12 and relation_count == 10, (len(related), relation_count)

    planned_alignment = [dict(row) for row in alignments]
    planned_target = next(
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    previous_note = planned_target.get("resolution_note", "")
    assert "No external identity source was accessed; KU assignment remains for S4." in previous_note
    assert "S3 reuse review (2026-10-16)" not in previous_note
    planned_target["decision"] = "same"
    planned_target["ku_id"] = KU_ID
    planned_target["process_ref"] = "S3-full-book-2026-10-16"
    planned_target["resolution_note"] = (
        previous_note
        + " Prior S3 proposal retained for history: " + PRIOR_GROUP
        + ". S3 reuse review (2026-10-16): the candidate's index entry M.csv#26 and full-name anchors "
        "in ch.10 p.325, ch.13 p.340, and ch.20 pp.408–409 identify painter Francesco Maggiotto. "
        "The existing accepted KU card 04-knowledge/units/persons/francesco-maggiotto.md is titled "
        "Francesco Fedeli, detto il Maggiotto and already links Plate 68a's Francesco Maggiotto. "
        f"Treccani DBI ({TRECCANI_URL}) explicitly identifies Francesco Fedeli, detto il Maggiotto, "
        "born Venice 1738 and died Venice 1805-09-13, as a painter; it says he took the Maggiotto name "
        "from his painter father Domenico. Getty ULAN 500125012 lists Francesco Maggiotto, Fedeli, "
        "Francesco, and Magiotto/Majotto variants, an Italian painter/draftsman, Venice activity, and "
        "Domenico as father; its summary date 1750–1805 differs from Treccani's 1738–1805 while ULAN's "
        "contributing RKD source lists 1738–1805. Wikidata Q3080993 is already mapped to the accepted "
        "card. Exact forename, byname, Venice painter context, Pinelli/Doge subject context, and the "
        "biographical authorities support reuse of this KU rather than a duplicate. The separate "
        f"father KU {FATHER_KU} remains distinct. This person-level reuse does not merge the unresolved "
        "Doge-portrait work candidates cand-10042, cand-3352, or cand-4190."
    )

    used_alignment_ids = {
        int(match.group(1))
        for row in planned_alignment
        if (match := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))
    }
    next_id = max(used_alignment_ids, default=0) + 1
    authority_rows = [
        {
            "alignment_id": f"aln-{next_id:04d}",
            "candidate_id": CANDIDATE,
            "ku_id": KU_ID,
            "external_source": "Treccani DBI",
            "external_id": TRECCANI_URL,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity only: Treccani DBI names Francesco Fedeli, detto il Maggiotto (Magiotto, "
                "Majotto), born in Venice in 1738 and deceased there on 1805-09-13; it states that he "
                "took the byname from his painter father Domenico and identifies him as a painter."
            ),
        },
        {
            "alignment_id": f"aln-{next_id + 1:04d}",
            "candidate_id": CANDIDATE,
            "ku_id": KU_ID,
            "external_source": "Getty ULAN",
            "external_id": ULAN_ID,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity only: ULAN 500125012 lists Maggiotto, Francesco; Francesco Maggiotto; "
                "Fedeli, Francesco; Magiotto, Francesco; and Majotto, Francesco, as an Italian painter "
                "and draftsman active in Venice, and lists Domenico Maggiotto as his father. ULAN's "
                "summary gives 1750–1805, while its contributing RKD biography gives 1738–1805; retain "
                "this date variation against Treccani's 1738–1805."
            ),
        },
        {
            "alignment_id": f"aln-{next_id + 2:04d}",
            "candidate_id": CANDIDATE,
            "ku_id": KU_ID,
            "external_source": "Wikidata",
            "external_id": WIKIDATA_ID,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity only: Q3080993 is the Wikidata identity already recorded on the accepted "
                "Francesco Fedeli, detto il Maggiotto card; this candidate maps to that same person KU."
            ),
        },
    ]
    planned_alignment.extend(authority_rows)

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    external_count = sum(bool(row.get("external_source")) for row in planned_alignment)
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"),
        stats,
        totals,
        len(manifest),
    )
    next_result, count_updates = re.subn(
        r"\d+(?=条外部身份记录单独保留)",
        str(external_count),
        next_result,
        count=1,
    )
    assert count_updates == 1, "could not refresh external identity record count"
    marker = "。各组来源、身份边界和映射更正见[过程记录]"
    assert next_result.count(marker) == 1
    result_insert = (
        f"；person 候选 {CANDIDATE}（Maggiotto, Francesco）复用"
        "[弗朗切斯科·费代利（又称马焦托）人物卡](../units/persons/francesco-maggiotto.md)，"
        "10条关系候选留待 S6" + marker
    )
    next_result = next_result.replace(marker, result_insert, 1)

    note = (
        f"\n### S3 person：{CANDIDATE} 复用弗朗切斯科·费代利人物 KU（{DATE}）\n\n"
        f"- 索引候选 {CANDIDATE}（M.csv#26，pp.325、340、408、409）原记为 new 组 {PRIOR_GROUP}；"
        f"现裁决为 same → {KU_ID}，复用既有人物卡 {CARD_REL}，不新建重复 KU。第10章 p.325 与第13章 p.340 均以全名 Francesco Maggiotto 指称画家；"
        "第13章记其与 Maffeo Pinelli 的交往及 Doge 肖像等创作，第20章后记再以全名记至少六幅为 Pinelli 绘制的 Doge 肖像。"
        "既有人物卡已由图版68a的 Francesco Maggiotto 全名锚点、Treccani DBI《FEDELI, Francesco, detto il Maggiotto》及 Wikidata Q3080993 支持。"
        "Treccani 记其1738年生于威尼斯、1805年9月13日卒于威尼斯，并说明其 Maggiotto 别名来自画家父亲 Domenico。Getty ULAN 500125012 列 Francesco Maggiotto、Fedeli, Francesco、Magiotto/Majotto 等形式，"
        "记意大利画家/绘图者、威尼斯活动及父亲 Domenico；其总述日期1750–1805与 Treccani 不同，但所汇 RKD 传记项也有1738–1805。保留日期差异，不据此拆分身份。"
        f"父亲仍由独立人物 KU {FATHER_KU} 表示。人物身份复用不合并 Doge 肖像作品候选 cand-10042、cand-3352、cand-4190；这些作品边界仍按各自 S3 待证说明处理。\n"
        f"- 涉及该候选的12条 S2 陈述中10条标为关系候选，留待 S6 逐条审查；没有新增正式关系或 S5 补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    assert f"### S3 person：{CANDIDATE} 复用弗朗切斯科·费代利人物 KU（{DATE}）" not in knowledge_text
    next_knowledge = knowledge_text + note

    outputs = {
        ALIGNMENT: None,
        RESULT: next_result,
        KNOWLEDGE: next_knowledge,
    }
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=alignment_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(planned_alignment)
    outputs[ALIGNMENT] = buffer.getvalue()

    assert not any(
        path.with_name(path.name + BACKUP_SUFFIX).exists()
        for path in outputs
    )
    if args.dry_run:
        for path, updated in outputs.items():
            current = path.read_text(encoding="utf-8-sig")
            diff = difflib.unified_diff(
                current.splitlines(keepends=True),
                updated.splitlines(keepends=True),
                fromfile=str(path.relative_to(ROOT)),
                tofile=str(path.relative_to(ROOT)) + " (updated)",
                n=2,
            )
            print("".join(diff), end="")
        print(
            f"dry-run passed: {CANDIDATE} -> same {KU_ID}; existing_card={CARD_REL}; "
            f"related_statements={len(related)}; relation_candidates_pending={relation_count}; "
            f"external_records={external_count}; registered={totals['registered_groups']}/"
            f"{totals['registered_members']}; pending={totals['pending_groups']}/"
            f"{totals['pending_members']}; manifest={len(manifest)} (unchanged)"
        )
        return 0

    backups: list[tuple[Path, Path]] = []
    for path in outputs:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        shutil.copy2(path, backup)
        backups.append((path, backup))
    try:
        for path, updated in outputs.items():
            path.write_text(updated, encoding="utf-8-sig", newline="\n")
    except Exception:
        for path, backup in backups:
            shutil.copy2(backup, path)
        raise
    print(
        f"applied: {CANDIDATE} -> same {KU_ID}; relation_candidates_pending={relation_count}; "
        f"external_records={external_count}; registered={totals['registered_groups']}/"
        f"{totals['registered_members']}; pending={totals['pending_groups']}/"
        f"{totals['pending_members']}; manifest={len(manifest)} unchanged; "
        f"recovery_backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
