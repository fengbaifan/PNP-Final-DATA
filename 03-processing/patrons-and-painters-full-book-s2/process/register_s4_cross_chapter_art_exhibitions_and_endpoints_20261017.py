from __future__ import annotations

import argparse
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
ENTITY_PATH = TABLES / "entity-candidates.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

TARGETS = [
    {
        "group": "sg3-term-artexhibitions",
        "candidates": ["cand-0132", "cand-0134", "cand-0137"],
        "ku": "units/terms/art-exhibitions",
        "card": "04-knowledge/units/terms/art-exhibitions.md",
        "type": "term",
        "name_zh": "艺术展览",
        "name_en": "Art exhibitions",
        "relations": [
            "st-chp10-p330-venetian-exhibition-sites-open",
            "st-chp10-p331-piazza-display-completion",
            "st-chp5-p125-exhibition-religious-calendar",
            "st-chp5-p125-exhibitions-usefulness",
            "st-chp8-p211-andrea-lent-pictures-to-salvatore-exhibitions",
            "st-chp5-p125-corpus-domini-display-association",
            "st-chp5-p125-exhibitions-attracted-connoisseurs",
        ],
    },
    {
        "group": "sg3-event-cand-6024",
        "candidates": ["cand-6024"],
        "ku": "units/events/corpus-domini-feast",
        "card": "04-knowledge/units/events/corpus-domini-feast.md",
        "type": "event",
        "name_zh": "Corpus Domini 节期",
        "name_en": "Corpus Domini Feast",
        "relations": [
            "st-chp5-p125-corpus-domini-display-association",
            "st-chp5-p135-van-laer-may-have-sold-scenes-at-corpus-domini",
            "st-chp8-p233-sacconi-corpus-domini-exhibition",
        ],
    },
    {
        "group": "sg3-place-cand-9856",
        "candidates": ["cand-9856"],
        "ku": "units/places/piazza-s-marco-venice",
        "card": "04-knowledge/units/places/piazza-s-marco-venice.md",
        "type": "place",
        "name_zh": "威尼斯圣马可广场",
        "name_en": "Piazza S. Marco, Venice",
        "relations": [
            "st-chp10-p330-venetian-exhibition-sites-open",
            "st-chp10-p331-piazza-display-completion",
        ],
    },
]


def sources_for(target: dict) -> list[dict]:
    common = {"citation": BOOK_CITATION, "evidence_ref": {"doc_id": "patrons-and-painters"}}
    if target["type"] == "term":
        items = [
            ("第5章；印刷页125；OCR L53", "Haskell describes the gradual extension of art exhibitions and their broad public role.", "line 53", "Far more effective than any kind of dealer in bringing the artist into contact with a wider public was the gradual extension of art exhibitions.", "02-sources/02-Markdown/05_CHP-5_sec_i.md", "line 53"),
            ("第8章；印刷页211；OCR L85–86", "Haskell says Andrea del Rosso frequently lent pictures to exhibitions at S. Salvatore in Lauro.", "lines 85–86", "frequently lent pictures to the exhibitions at S. Salvatore in Lauro", "02-sources/02-Markdown/08_CHP-8_sec_i.md", "lines 85–86"),
            ("第10章；印刷页330–331；OCR L264、270", "Haskell identifies art-display sites in Venice, including casual display at the Piazza S. Marco site and more systematic exhibitions at S. Rocco.", "lines 264, 270", "there were two spots in the city which were given over to art exhibitions. In the Piazza S. Marco", "02-sources/02-Markdown/10_CHP-10_sec_ii.md", "lines 264, 270"),
        ]
    elif target["type"] == "event":
        items = [
            ("第5章；印刷页125；OCR L53", "Haskell says Corpus Domini was especially associated with picture display, while noting it was not the only such occasion.", "line 53", "The feast of Corpus Domini above all was associated with the display of pictures, but it certainly had no monopoly.", "02-sources/02-Markdown/05_CHP-5_sec_i.md", "line 53"),
            ("第5章；印刷页135；OCR L30", "Haskell tentatively mentions scenes possibly sold at the fairs of Corpus Domini.", "line 30", "at the fairs of Corpus Domini, perhaps", "02-sources/02-Markdown/05_CHP-5_sec_iii.md", "line 30"),
            ("第8章；印刷页233；OCR L277", "Haskell says Ferdinand arranged for Sacconi's pictures to be exhibited on Corpus Domini; the pictures and a specific venue are not identified.", "line 277", "He arranges for his pictures to be exhibited on Corpus Domini", "02-sources/02-Markdown/08_CHP-8_sec_ii.md", "line 277"),
            ("第8章；印刷页240；OCR L355", "Haskell says pictures had been exhibited during Corpus Domini processions in Florence and many other Italian cities.", "line 355", "Pictures had been exhibited in Florence, as in many other Italian cities, on the occasion of the Corpus Domini processions", "02-sources/02-Markdown/08_CHP-8_sec_ii.md", "line 355"),
        ]
    else:
        items = [
            ("第10章；印刷页330；OCR L264", "Haskell locates one Venetian exhibition site at Piazza S. Marco beside a projecting wing of the Procuratie Nuove.", "line 264", "In the Piazza S. Marco, by the left-hand projecting wing of the Procuratie Nuove adjoining", "02-sources/02-Markdown/10_CHP-10_sec_ii.md", "line 264"),
            ("第10章；印刷页331；OCR L270", "The continuation identifies the adjoining church as S. Geminiano and says painters sometimes showed work there casually; it does not place the display inside the church.", "line 270", "the church of S. Geminiano, painters sometimes chose to show their work to the public in a thoroughly casual way", "02-sources/02-Markdown/10_CHP-10_sec_ii.md", "line 270"),
        ]
    result = []
    for location, summary, span, quote, source_file, ref_span in items:
        row = dict(common)
        row.update({
            "location": location,
            "sentence_summary": summary,
            "original_quotes": [{"source_span": span, "text": quote}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": source_file, "source_span": ref_span},
        })
        result.append(row)
    return result


def make_card(target: dict) -> str:
    title = f"{target['name_zh']}（{target['name_en']}）"
    fm = {
        "title": title,
        "name_en": target["name_en"],
        "type": target["type"],
        "evidence_status": "source_backed",
        "sources": sources_for(target),
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": PROCESS_REF,
    }
    frontmatter = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    if target["type"] == "term":
        body = """## 内容

### 描述

**中文：** 本卡记录哈斯克尔书中“art exhibitions”作为面向公众的绘画展示活动这一一般概念。第5章讨论其逐渐扩展，第8章举出 S. Salvatore in Lauro 的展览，第10章区分威尼斯不同地点的随意展示与较有组织的展览。书后索引将 `cand-0132`（S. Bartolommeo）、`cand-0134`（San Salvatore in Lauro）和 `cand-0137`（Piazza S. Marco）列在同一术语主项下；本卡不把这些地点或个别活动并入术语。

**English:** This card records “art exhibitions” as the general practice of displaying pictures to a public in Haskell's account. Chapter 5 discusses its gradual extension, Chapter 8 mentions exhibitions at S. Salvatore in Lauro, and Chapter 10 distinguishes casual display at one Venetian site from more systematic exhibitions elsewhere. The book index places `cand-0132` (S. Bartolommeo), `cand-0134` (San Salvatore in Lauro), and `cand-0137` (Piazza S. Marco) under the same term entry. The venues and particular activities remain separate.

### 身份边界

三个 S3 同组候选共同映射至本 term KU；不与具体展览系列、节庆、地点或组织举办的程序合并。既有 Ferdinand art-exhibition guidance procedure 仍为独立 KU。

The three S3 group members map to this single term KU. It is not merged with a particular exhibition series, feast, venue, or organizing procedure. The existing Ferdinand art-exhibition guidance procedure remains a separate KU.

## 关系与证据

7条直接 S2 `relation_candidate` 留待 S6：`st-chp10-p330-venetian-exhibition-sites-open`, `st-chp10-p331-piazza-display-completion`, `st-chp5-p125-exhibition-religious-calendar`, `st-chp5-p125-exhibitions-usefulness`, `st-chp8-p211-andrea-lent-pictures-to-salvatore-exhibitions`, `st-chp5-p125-corpus-domini-display-association`, `st-chp5-p125-exhibitions-attracted-connoisseurs`。未决端点 `cand-11715`、`cand-11717`、`cand-11720` 保持待证；本卡未新增正式关系。
"""
    elif target["type"] == "event":
        body = """## 内容

### 描述

**中文：** 本卡记录 Haskell 所称 Corpus Domini 节期及相关游行这一重复节庆语境。第5章称该节期尤其与图像展示相关，但并非唯一场合；第8章提到佛罗伦萨及其他意大利城市曾在 Corpus Domini 游行期间展出绘画。Haskell 另称 Ferdinand 曾安排 Sacconi 的画作在 Corpus Domini 展出，并以“perhaps”限定 Van Laer 在相关集市售画的说法。本卡表示节期语境，不代表某一届展览、特定作品或确定地点。

**English:** This card records the recurring feast and procession context referred to as Corpus Domini in Haskell's account. Chapter 5 says the feast was especially associated with picture display but was not the only occasion; Chapter 8 mentions pictures exhibited during Corpus Domini processions in Florence and other Italian cities. Haskell also says Ferdinand arranged for Sacconi's pictures to be shown on Corpus Domini and tentatively suggests that Van Laer may have sold scenes at its fairs. This unit denotes the feast context, not a single exhibition, specific picture, or fixed venue.

### 活动性质与时间

- 活动性质：具名节期及其游行语境；本卡不合并各地、各届展览。
- 日期或周期：本组来源未给出可据以确定的具体展览日期；不据候选关系补定日期。
- 地点：书中分别提到佛罗伦萨及其他意大利城市，未限定单一举办地点。

## 关系与证据

3条直接 S2 `relation_candidate` 留待 S6：`st-chp5-p125-corpus-domini-display-association`, `st-chp5-p135-van-laer-may-have-sold-scenes-at-corpus-domini`, `st-chp8-p233-sacconi-corpus-domini-exhibition`。保留 Haskell 的限定语；本卡未新增正式关系。
"""
    else:
        body = """## 内容

### 描述

**中文：** 威尼斯 Piazza S. Marco 是 Haskell 在第10章所述的一个艺术展示地点。第330页把它定位在 Procuratie Nuove 左侧突出翼楼旁；续页指出相邻地标是 S. Geminiano 教堂，并说画家有时在该处以随意方式向公众展示作品。原文没有说展示发生在教堂内部，也没有将广场本身描述为展览组织机构。

**English:** Piazza S. Marco in Venice is one of the art-display locations described by Haskell in Chapter 10. Page 330 places it beside the left-hand projecting wing of the Procuratie Nuove; the continuation identifies the adjoining landmark as the church of S. Geminiano and says painters sometimes showed work to the public there in a casual manner. The text does not place the display inside the church or describe the piazza as an exhibition organization.

### 地点信息

- 类型：威尼斯城市广场；依据：Haskell，第10章 p.330–331。
- 书内定位：Procuratie Nuove 翼楼旁，邻近 S. Geminiano 教堂；依据：Haskell，第10章 p.330–331。

## 关系与证据

2条直接 S2 `relation_candidate` 留待 S6：`st-chp10-p330-venetian-exhibition-sites-open`、`st-chp10-p331-piazza-display-completion`。地点卡不据此写入正式关系。
"""
    return f"---\n{frontmatter}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(ENTITY_PATH)
    alignment_fields, alignment = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignment if not row.get("external_source")}
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_lines = accepted.splitlines()

    targets_by_candidate = {cid: target for target in TARGETS for cid in target["candidates"]}
    assert len(targets_by_candidate) == sum(len(t["candidates"]) for t in TARGETS)
    for target in TARGETS:
        assert target["ku"] not in manifest_by_id, f"KU already exists: {target['ku']}"
        assert not (ROOT / target["card"]).exists(), f"card already exists: {target['card']}"
        assert f"- {target['card']}" not in accepted_lines, f"accepted entry already exists: {target['card']}"
        assert target["type"] in {"term", "event", "place"}
        for cid in target["candidates"]:
            assert cid in candidate_by_id and cid in alignment_by_id, f"missing S3 candidate/alignment: {cid}"
            candidate, decision = candidate_by_id[cid], alignment_by_id[cid]
            assert candidate["suggested_type"] == target["type"], f"type mismatch for {cid}"
            assert decision["decision"] == "new", f"not S3 new: {cid}"
            assert not decision.get("ku_id"), f"already mapped: {cid}"
            assert sync.get_group(decision.get("resolution_note", "")) == target["group"], f"group mismatch: {cid}"

    planned_alignment = [dict(row) for row in alignment]
    planned_manifest = [dict(row) for row in manifest]
    for target in TARGETS:
        for row in planned_alignment:
            if row.get("candidate_id") in target["candidates"]:
                row["ku_id"] = target["ku"]
                row["resolution_note"] = (row.get("resolution_note", "") +
                    f" S4 registration: mapped {target['group']} to {target['ku']}.")
        planned_manifest.append({
            "ku_id": target["ku"],
            "type": target["type"],
            "canonical_name": target["name_zh"],
            "name_en": target["name_en"],
            "source_task": TASK,
            "card_path": target["card"],
        })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s4-cross-chapter-art-exhibitions-and-endpoints\"></a>\n\n"
        "### S4 跨章术语及直接端点登记：Art exhibitions（2026-10-17）\n\n"
        "`cand-0132`（A.csv#133，p.125）、`cand-0134`（A.csv#135，pp.128–129、211）和 `cand-0137` "
        "（A.csv#138，p.330）沿用同一 S3 `new` 组 `sg3-term-artexhibitions`，共同映射至 "
        "`units/terms/art-exhibitions`。第5章的一般展览论述、第8章 S. Salvatore in Lauro 展览及第10章威尼斯展示语境 "
        "支持同一术语概念；具体活动与场地分立。\n\n"
        "同批登记两个直接关系端点：`cand-6024`（Corpus Domini，S3 event new）→ `units/events/corpus-domini-feast`；"
        "`cand-9856`（Piazza S. Marco，S3 place new）→ `units/places/piazza-s-marco-venice`。前者记录节期／游行语境，"
        "不推定特定展览日期；后者按 p.330–331 记录广场地点，不将相邻 S. Geminiano 教堂当作展览室。\n\n"
        "术语组7条、Corpus Domini 组3条、Piazza S. Marco 组2条直接 relation_candidate 均留待 S6，未写入正式关系。"
        "术语关系中的未决端点 `cand-11715`、`cand-11717`、`cand-11720` 保持 S3 undecided；其余候选及既有对象维持原决定。"
        f"\n\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 跨章术语及直接端点登记（2026-10-17）\n\n"
        "`cand-0132`、`cand-0134`、`cand-0137` 作为同一跨章 S3 术语组登记为 [艺术展览](../units/terms/art-exhibitions.md)；"
        "`cand-6024` 登记为 [Corpus Domini 节期](../units/events/corpus-domini-feast.md)；"
        "`cand-9856` 登记为 [威尼斯圣马可广场](../units/places/piazza-s-marco-venice.md)。"
        "7、3、2条直接关系候选分别保留待 S6；未决艺术家群体、观众群体及圣人瞻礼日／游行类别不改裁决。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    for target in TARGETS:
        card = target["card"]
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > card),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {card}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 dry-run passed: groups={len(TARGETS)}; candidates={sum(len(t['candidates']) for t in TARGETS)}")
        print("types=term,event,place; preserved=all S3 decisions; formal_relations_added=0")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    for target in TARGETS:
        (ROOT / target["card"]).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / target["card"]).write_text(make_card(target), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups={len(TARGETS)}; registered={sync.fmt(totals['registered_groups'])}/"
        f"{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/"
        f"{sync.fmt(totals['pending_members'])}; manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
