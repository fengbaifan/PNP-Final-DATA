from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import s3_reuse_sassoferrato_candidates_20261017 as summary_tools
import register_s4_valmarana_cluster_batch_20261015 as card_writer

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

GROUP = "new-person:chigi-mario-1e3f6f6032"
MEMBERS = ("cand-0674",)
KU_ID = "units/persons/mario-chigi"
CARD_PATH = "04-knowledge/units/persons/mario-chigi.md"
DATE = "2026-10-17"
ANCHOR = "s3-s4-person-mario-chigi-20261017"
TRECCANI_URL = "https://static.treccani.it/export/sites/default/catalogo/catalogo_prodotti/grandi_opere/biografia_nazionale/pdf/DBI88_Rosa_Salvatore.pdf"
TRECCANI_SOURCE = "Treccani, Dizionario Biografico degli Italiani, vol. 88, s.v. Rosa, Salvatore"
DIRECT_RELATIONS = (
    "st-chp6-p154-don-mario-intervenes-for-rosa",
    "st-chp6-p154-don-mario-brother-of-pope",
    "st-chp6-p154-don-mario-implicated-in-rosa-interpretation",
    "st-chp6-p154-don-mario-father-of-flavio",
)
BT = chr(96)
QUOTE = (
    "‘The affair assumed such proportions’, wrote\nBaldinucci,1 ‘that the painter was on the point of having to explain the meaning of his picture in prison’, "
    "had it not been for the intervention of Don Mario Chigi, the Pope’s brother and, incidentally, one of those most obviously implicated in Rosa’s satirical interpretation of Fortune. -\n"
    "There is a double irony in Don Mario’s generous move, for at about this time his son, Cardinal Flavio Chigi, was commissioning from a second-rate Sienese painter,\n"
    "Bernardino Mei, a ceiling fresco of Fortune under the control of Virtue."
)

RECORD = {
    "name_zh": "马里奥·基吉",
    "name_en": "Mario Chigi",
    "description_zh": (
        "哈斯克尔在第6章 p.154 称 Don Mario Chigi 为教皇之弟；索引进一步标为教皇亚历山大七世之弟。正文转述 Baldinucci 对 Salvator Rosa 画作争议的记载，并说 Don Mario 的介入使画家免于在监狱解释画意。"
        "哈斯克尔还把 Don Mario 列为其对《Fortune》讽刺解读明显影射的人物，并称红衣主教 Flavio Chigi 是其子。介入、亲缘与影射均作为原书关系候选保留，尚未写成正式关系；“double irony”是作者的修辞判断。"
    ),
    "description_en": (
        "On p. 154 of chapter 6, Haskell calls Don Mario Chigi the Pope’s brother; the index specifies Alexander VII. Recounting Baldinucci on the controversy over Salvator Rosa’s picture, "
        "Haskell says Don Mario’s intervention spared the painter from having to explain the image in prison. Haskell also names Don Mario among those most obviously implicated in his reading of the picture as a satire on Fortune, "
        "and identifies Cardinal Flavio Chigi as his son. The intervention, kinship, and implication remain source-attributed relation candidates, not formal relations; “double irony” is Haskell’s rhetorical interpretation."
    ),
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


def get_group(note):
    match = re.search(r"group=([^;| ]+)", note)
    return match.group(1) if match else None


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"expected one {label}; found {count}")
    return text.replace(old, new, 1)


def make_card():
    source = card_writer.source(
        "6", "154", "06_CHP-6_sec_i.md", "94–96", QUOTE,
        "哈斯克尔转述 Baldinucci 对 Rosa 画作争议的记载，称 Don Mario Chigi 的介入使画家不必在监狱解释画意；同段称其为教皇之弟、Fortune 讽刺的影射对象之一，并称 Flavio Chigi 为其子。作者另以 double irony 概括相邻叙述。",
    )
    frontmatter = {
        "title": f"{RECORD['name_zh']}（{RECORD['name_en']}）",
        "name_en": RECORD["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [{
            "citation": card_writer.BOOK_CITATION,
            "location": "第6章，印刷页154；OCR L94–96",
            "sentence_summary": source["summary"],
            "original_quotes": [{"source_span": "lines 94–96", "text": QUOTE}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
                "source_span": "lines 94–96; print p. 154",
            },
        }],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = card_writer.yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {RECORD['description_zh']}

**English:** {RECORD['description_en']}

### 名称

中文显示名及英文显示名见卡片标题；原书称谓 Don Mario Chigi 按来源引文保留，不在本卡推定其为正式贵族头衔。

The bilingual display names appear in the card title. The source form “Don Mario Chigi” is preserved in the quotation; this card does not treat Don as a verified formal noble title.

### 身份核对

Treccani《意大利人传记辞典》第88卷 Salvator Rosa 条目[PDF]({TRECCANI_URL})（访问于 {DATE}）提到 1659 年 Rosa 展出讽刺 Chigi 教廷裙带关系的《Fortune》，并称 Mario Chigi（教皇之弟）为 Rosa 辩护、使其免受争议指控。该姓名、教皇亲缘及同一画作争议与本书 p.154 的 Don Mario Chigi 相合；此来源用于身份比对，不把外部生平字段或精确关系写入卡片。

### 身份边界

中文：本卡仅指第6章 p.154 的 Don Mario Chigi／索引所称亚历山大七世之弟。不要与其子 Cardinal Flavio Chigi 或其他 Chigi 家族成员合并。

English: This card refers to Don Mario Chigi in chapter 6 p. 154, indexed as Alexander VII’s brother. Keep him distinct from his son Cardinal Flavio Chigi and other members of the Chigi family.

## 关系与证据

本卡未新增正式关系。4条直接 S2 关系候选待 S6：{BT}st-chp6-p154-don-mario-intervenes-for-rosa{BT}（Baldinucci 引述经 Haskell 转述；没有说 Rosa 实际入狱或被正式起诉）；{BT}st-chp6-p154-don-mario-brother-of-pope{BT}（正文称教皇之弟，索引指明 Alexander VII）；{BT}st-chp6-p154-don-mario-implicated-in-rosa-interpretation{BT}（Haskell 对讽刺影射的解释，不是 Mario 本人留下的反应证据）；{BT}st-chp6-p154-don-mario-father-of-flavio{BT}（原书称 Cardinal Flavio Chigi 为其子）。另有非关系性修辞陈述 {BT}st-chp6-p154-double-irony-of-don-mario-intervention{BT}，保留为 Haskell 对段落并置的评价，不转成实体关系。
"""


def s3_note(old_note):
    return (
        f"source_ref=candidate=cand-0674;index_entry=C.csv#198;index_pages=154; group={GROUP}; "
        "S3 identity review 2026-10-17: retain new as one source-local person. Index and p.154 provide the full form Don Mario Chigi and identify him as Alexander VII’s brother; "
        "the person manifest contains no matching Mario Chigi KU. Treccani DBI vol. 88, entry Rosa, Salvatore ("
        f"{TRECCANI_URL}; accessed {DATE}) describes Rosa’s 1659 painting Fortune as a satire on Chigi nepotism and identifies Mario Chigi, the Pope’s brother, as the person who defended Rosa in that controversy. "
        "The name, papal kinship, and same Fortune-picture controversy support identity; this corroborates identity only and does not validate each S2 relation candidate or Haskell’s interpretive claims. "
        "prior_resolution_note=" + old_note
    )


def update_process(text, registered_groups, registered_members, pending_groups, pending_members, manifest_count):
    if f'<a id="{ANCHOR}"></a>' in text:
        return text
    entry = f"""

<a id="{ANCHOR}"></a>

### S3→S4 person：Don Mario Chigi 直接关系端点身份组登记（{DATE}）

cand-0674（C.csv#198，p.154）保留 new 并登记为 {GROUP}／{KU_ID}。索引全名及括注将 Don Mario Chigi 标为 Pope Alexander VII 之弟；正文 p.154 有 Don Mario Chigi 全名及其后回指。人物 manifest 未见同名 KU。

外部身份比对使用 Treccani DBI 第88卷 Salvator Rosa 条目（[PDF]({TRECCANI_URL})，访问：{DATE}）。该条目记载 Rosa 1659 年展出的《Fortune》被读作对 Chigi 教廷裙带关系的讽刺，并称 Mario Chigi（教皇之弟）为画家辩护、使其免受指控。姓名、教皇亲缘和同一画作争议与 Haskell p.154 的 Don Mario 对应。此来源只支持人物身份，不替代 S6 关系裁决，也不把 Rosa 是否实际面临监禁或法律指控写成事实。

S4 新建[马里奥·基吉人物卡](../../../04-knowledge/units/persons/mario-chigi.md)，候选 cand-0674 映射至 {KU_ID}；外部身份比对作为单独 alignment 行。4条直接 S2 关系候选（介入、兄弟、影射、父子）仍待 S6；作者的 double irony 解释保留为非关系陈述，未新增正式边。

S4 当前登记 {registered_groups} 组／{registered_members} 条候选映射；待登记 {pending_groups} 组／{pending_members} 条映射；KU 总数 {manifest_count}。
"""
    return text.rstrip() + entry


def update_result(text, planned_alignment, planned_manifest, planned_stats):
    candidate_rows = [row for row in planned_alignment if not row.get("external_source")]
    registered_groups = sum(row["registered_groups"] for row in planned_stats.values())
    pending_groups = sum(row["pending_groups"] for row in planned_stats.values())
    pending_members = sum(row["pending_candidates"] for row in planned_stats.values())
    pending_new = sum(1 for row in planned_alignment if row["decision"] == "new" and not row.get("ku_id"))
    external_count = sum(1 for row in planned_alignment if row.get("external_source"))

    text = replace_once(
        text,
        "S4 已登记523组、映射653条成员候选；尚待登记4,281组、4,325条映射。",
        f"S4 已登记{registered_groups:,}组、映射{sum(s['new_candidates'] for s in planned_stats.values()) - pending_members:,}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。",
        "S4 top-line counts",
    )
    text = replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,542 KU", f"| [KU 登记](../tables/ku-manifest.csv) | {len(planned_manifest):,} KU", "manifest count")
    align_pattern = re.compile(r"(\| \[全书对齐\]\(\.\./tables/alignment\.csv\) \| )[\d,]+ 条：12,407 条候选决定记录及 [\d,]+ 条外部身份记录；候选决定数见下表 \|")
    text, n = align_pattern.subn(
        lambda match: match.group(1) + f"{len(planned_alignment):,} 条：12,407 条候选决定记录及 {external_count:,} 条外部身份记录；候选决定数见下表 |",
        text,
        count=1,
    )
    if n != 1:
        raise AssertionError(f"alignment count row update matches: {n}")

    old_warning = re.compile(
        "审计警告中的[\\d,]+条待登记 " + re.escape(BT) + "decision=new" + re.escape(BT) +
        " alignment 行，含[\\d,]+条候选决定映射（[\\d,]+组）和[\\d,]+条外部身份记录。"
    )
    new_warning = (
        f"审计警告中的{pending_new:,}条待登记 {BT}decision=new{BT} alignment 行，含{pending_members:,}条候选决定映射"
        f"（{pending_groups:,}组）和15条外部身份记录。"
    )
    text, n = old_warning.subn(new_warning, text, count=1)
    if n != 1:
        raise AssertionError(f"audit warning count update matches: {n}")

    start = text.find("| 类型 | same（候选→KU） | new（候选／组） | S4 新组（已登记／待登记；待登候选） | conflict | excluded | undecided |")
    end = text.find("\n\n本轮新增的 archive 身份组包括：", start)
    if start < 0 or end < 0:
        raise AssertionError("S3/S4 type summary table not found")
    text = text[:start] + summary_tools.type_table(planned_stats, candidate_rows) + text[end:]

    text = replace_once(
        text,
        "S4当前登记523组/653条候选映射；待登记4,281组/4,325条；KU总数1,542。",
        f"S4当前登记{registered_groups:,}组/{sum(s['new_candidates'] for s in planned_stats.values()) - pending_members:,}条候选映射；待登记{pending_groups:,}组/{pending_members:,}条；KU总数{len(planned_manifest):,}。",
        "S4 current result count",
    )
    heading = "### S3→S4 person：Don Mario Chigi 直接关系端点身份组登记（2026-10-17）"
    if heading not in text:
        text = text.rstrip() + f"""

{heading}

cand-0674（C.csv#198，p.154）登记为[马里奥·基吉人物卡](../units/persons/mario-chigi.md)。Treccani DBI 第88卷 Rosa 传记记述同一《Fortune》画作争议、Mario Chigi 的教皇亲属身份及其为 Rosa 辩护，支持与本书 p.154 的人物相同；外部来源只作身份比对。

4条直接 S2 关系候选留待 S6；作者关于 double irony 的修辞解释不转为关系。本卡未新增正式边。

S4 当前登记 {registered_groups:,} 组／{sum(s['new_candidates'] for s in planned_stats.values()) - pending_members:,} 条候选映射；待登记 {pending_groups:,} 组／{pending_members:,} 条映射；KU 总数 {len(planned_manifest):,}。
"""
    return text


def main():
    parser = argparse.ArgumentParser(description="Register Don Mario Chigi as a source-backed person KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == MEMBERS[0])
    candidate_rows = [row for row in alignments if row.get("candidate_id") == MEMBERS[0] and not row.get("external_source")]
    ext_rows = [row for row in alignments if row.get("candidate_id") == MEMBERS[0] and row.get("external_source") == TRECCANI_SOURCE]
    card_path = ROOT / CARD_PATH
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    if card_path.exists() and len(candidate_rows) == 1 and candidate_rows[0].get("ku_id") == KU_ID:
        assert CARD_PATH in accepted_text and any(row["ku_id"] == KU_ID for row in manifest)
        assert len(ext_rows) == 1 and ext_rows[0].get("external_id") == TRECCANI_URL
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}")
        return 0

    assert len(manifest) == 1542, f"unexpected manifest count: {len(manifest)}"
    assert not card_path.exists() and CARD_PATH not in accepted_text
    assert candidate["suggested_type"] == "person"
    assert len(candidate_rows) == 1
    candidate_alignment = candidate_rows[0]
    assert candidate_alignment["decision"] == "new" and not candidate_alignment.get("ku_id")
    assert get_group(candidate_alignment["resolution_note"]) == GROUP
    assert not ext_rows
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)
    assert not any(row["type"] == "person" and "mario chigi" in (row["canonical_name"] + " " + row["name_en"] + " " + row["card_path"]).casefold() for row in manifest)

    before_stats = summary_tools.compute_stats(alignments, candidates)
    assert (sum(s["registered_groups"] for s in before_stats.values()), sum(s["pending_groups"] for s in before_stats.values()), sum(s["pending_candidates"] for s in before_stats.values())) == (523, 4281, 4325)
    assert len(alignments) == 12641 and sum(1 for row in alignments if row.get("external_source")) == 234

    direct = {}
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("statement_id") in DIRECT_RELATIONS:
                direct[statement["statement_id"]] = statement
    assert set(direct) == set(DIRECT_RELATIONS)
    assert all((row.get("qualifiers") or {}).get("relation_candidate") is True for row in direct.values())
    quote_path = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_i.md"
    assert QUOTE in quote_path.read_text(encoding="utf-8-sig")

    planned_alignment = [dict(row) for row in alignments]
    candidate_row = next(row for row in planned_alignment if row["alignment_id"] == candidate_alignment["alignment_id"])
    candidate_row["ku_id"] = KU_ID
    candidate_row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    candidate_row["resolution_note"] = s3_note(candidate_row["resolution_note"]) + f" S4 registration: mapped {GROUP} to {KU_ID}."
    next_id = max(int(row["alignment_id"].removeprefix("aln-")) for row in planned_alignment if row["alignment_id"].removeprefix("aln-").isdigit()) + 1
    planned_alignment.append({
        "alignment_id": f"aln-{next_id:04d}",
        "candidate_id": MEMBERS[0],
        "ku_id": KU_ID,
        "external_source": TRECCANI_SOURCE,
        "external_id": TRECCANI_URL,
        "decision": "same",
        "accessed_date": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
        "legacy_ku_id": "",
        "resolution_note": (
            "Identity corroboration only: Treccani DBI vol. 88, entry Rosa, Salvatore, says that Mario Chigi, the Pope’s brother, defended Rosa over the 1659 Fortune satire on Chigi nepotism "
            "(PDF p. 6, lines 381–388; accessed 2026-10-17). The name, papal kinship, and same painting controversy match Haskell ch. 6 p. 154. "
            "This corroborates identity only; it does not validate all S2 relation candidates, Haskell’s interpretation, or the prison wording."
        ),
    })

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": CARD_PATH,
    }]
    assert len(planned_manifest) == 1543
    planned_stats = summary_tools.compute_stats(planned_alignment, candidates)
    assert (sum(s["registered_groups"] for s in planned_stats.values()), sum(s["pending_groups"] for s in planned_stats.values()), sum(s["pending_candidates"] for s in planned_stats.values())) == (524, 4280, 4324)
    assert sum(1 for row in planned_alignment if row["decision"] == "new" and not row.get("ku_id")) == 4339
    assert len(planned_alignment) == 12642 and sum(1 for row in planned_alignment if row.get("external_source")) == 235

    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_PATH}")
    planned_accepted = "\n".join(accepted_lines) + "\n"
    process_text = update_process(
        PROCESS_PATH.read_text(encoding="utf-8-sig"),
        524, 654, 4280, 4324, len(planned_manifest),
    )
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), planned_alignment, planned_manifest, planned_stats)
    card_text = make_card()

    if args.dry_run:
        print(
            f"dry-run passed: group={GROUP} candidate=1 direct_relation_candidates=4 "
            "registered_groups_after=524 mapped_candidates_after=654 pending_groups_after=4280 pending_candidates_after=4324 "
            "manifest_after=1543 alignment_after=12642 external_records_after=235"
        )
        return 0

    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        f"applied: group={GROUP} ku={KU_ID} candidate=1 direct_relation_candidates=4 "
        "registered_groups=524 mapped_candidates=654 pending_groups=4280 pending_candidates=4324 "
        "manifest=1543 alignment=12642 external_records=235"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
