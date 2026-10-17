from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HERE))
import register_s4_person_endpoints_ciarpi_castello_conduitt_corelli_corradini_coypel_20261017 as base  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s4-person-endpoints-crescenzi-curli-dingley-errard-falcone-fanzago-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BT = chr(96)

base.DATE = DATE
base.ANCHOR = ANCHOR
base.PROCESS_REF = PROCESS_REF

TARGETS = [
    {
        "candidate": "cand-0870",
        "group": "new-person:crescenzi-paolo-pietro-b4e83b9a13",
        "ku": "units/persons/pietro-paolo-crescenzi",
        "card": "04-knowledge/units/persons/pietro-paolo-crescenzi.md",
        "name_zh": "彼得罗·保罗·克雷申齐",
        "name_en": "Pietro Paolo Crescenzi",
        "name_field": "索引名",
        "index_entry": "C.csv#404",
        "index_file": "C.csv",
        "index_name": "Crescenzi, Pietro Paolo",
        "index_page": "173",
        "source_fragments": ["His brother was a cardinal", "Moreover, both were devoted to the Spanish cause."],
        "book_sources": [{
            "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
            "source_span": "line 38; print p. 173",
            "location": "第7章 p.173；OCR L38",
            "summary": "正文称Giovanni Battista Crescenzi的兄弟为枢机，并以“both”指两兄弟；正文没有写出兄弟全名。书后索引另以“Crescenzi, Pietro Paolo”列出第173页。",
            "quote": "His brother was a cardinal",
        }],
        "description_zh": "本卡登记书后索引主项“Crescenzi, Pietro Paolo”（C.csv#404），索引定位第7章 p.173。该页正文点名Giovanni Battista Crescenzi，但只称其兄弟为枢机，没有写出兄弟姓名；因此本卡仅登记索引所列人物，不据此确认正文代词的指代。中文名为本项目工作音译。",
        "description_en": "This card records the index entry “Crescenzi, Pietro Paolo” (C.csv#404), which points to Chapter 7, p.173. The passage names Giovanni Battista Crescenzi but refers to his cardinal brother without giving that brother’s name; this card registers the indexed person and does not resolve the pronoun’s referent. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp7-p173-i05", "st-chp7-p173-i08"],
        "relation_context_zh": "Haskell以“both”概括两兄弟早期雇用Claude及支持西班牙事业；S2将相关陈述映射到本候选，但正文未明写Pietro Paolo。索引身份与该指代不作等同断言，两项候选留待S6。",
        "relation_context_en": "Haskell uses “both” for the brothers’ early employment of Claude and devotion to the Spanish cause. S2 maps those statements to this candidate, although the body does not name Pietro Paolo. The index identity is not treated as proof of that referent; both candidates remain for S6.",
        "statement_endpoints": [
            ("st-chp7-p173-i05", "cand-0870", "cand-0767", "employed_claude", "among the very first to employ Claude"),
            ("st-chp7-p173-i08", "cand-0870", "cand-4404", "was_devoted_to", "both were devoted to the Spanish cause"),
        ],
        "alignment_note": "索引主项明确支持新建人物KU；正文只称Giovanni Battista的兄弟为枢机，不据索引页码单独确认兄弟指代，相关S2候选留待S6。",
    },
    {
        "candidate": "cand-0896",
        "group": "new-person:curli-girolamo-e60c7adef7",
        "ku": "units/persons/girolamo-curli",
        "card": "04-knowledge/units/persons/girolamo-curli.md",
        "name_zh": "吉罗拉莫·库尔利",
        "name_en": "Girolamo Curli",
        "name_field": "索引名",
        "index_entry": "C.csv#430",
        "index_file": "C.csv",
        "index_name": "Curli, Girolamo",
        "index_page": "357n",
        "source_fragments": ["letter to Girolamo Curli"],
        "book_sources": [{
            "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
            "source_span": "line 201; print p. 357 n. 1",
            "location": "第14章 p.357 注1；OCR L201",
            "summary": "注1提及一封1751年11月20日写给Girolamo Curli的信，并称该信由A. Neri于1885年刊布；原信及刊本未独立查阅。",
            "quote": "See letter to Girolamo Curli of 20 November 1751 published by A. Neri, 1885.",
        }],
        "description_zh": "本卡登记索引名为Girolamo Curli的人物。第14章注1称有一封1751年11月20日写给Curli的信，并指向A. Neri于1885年的刊本；原信及刊本尚未独立查阅。中文名为本项目工作音译。",
        "description_en": "This card records the person indexed as Girolamo Curli. Chapter 14, note 1, cites a letter to Curli dated 20 November 1751 and a publication by A. Neri in 1885; neither the letter nor the publication was independently consulted. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp14-p357-note1-letter-addressed-to-curli"],
        "relation_context_zh": "日期、收信人及刊布信息来自Haskell的书目注释；信件与Neri刊本未独立查阅，S2候选留待S6。",
        "relation_context_en": "The date, addressee, and publication details come from Haskell’s bibliographic note; the letter and Neri publication were not independently consulted, so the S2 candidate remains for S6.",
        "statement_endpoints": [("st-chp14-p357-note1-letter-addressed-to-curli", "cand-10357", "cand-0896", "addressed_to", "letter to Girolamo Curli")],
    },
    {
        "candidate": "cand-0921",
        "group": "new-person:dingley-robert-65504f2aee",
        "ku": "units/persons/robert-dingley",
        "card": "04-knowledge/units/persons/robert-dingley.md",
        "name_zh": "罗伯特·丁格利",
        "name_en": "Robert Dingley",
        "name_field": "索引名",
        "index_entry": "D.csv#23",
        "index_file": "D.csv",
        "index_name": "Dingley, Robert",
        "index_page": "303",
        "source_fragments": ["Mr Robert Dingley asked for a picture"],
        "book_sources": [{
            "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
            "source_span": "line 406; print p. 303",
            "location": "第10章 p.303；OCR L406",
            "summary": "Haskell称Robert Dingley于1735年从伦敦写信给Rosalba Carriera，请她画一幅风格类似Winter的少女像，并要求不要告知Smith；段落没有证明该画后来完成。",
            "quote": "a Mr Robert Dingley asked for a picture",
        }],
        "description_zh": "本卡登记索引名为Robert Dingley的人物。第10章 p.303称他于1735年写信向Rosalba Carriera请求一幅风格类似Winter的少女像，并要求不要告知Smith；Haskell转引的请求不证明Carriera完成了该画。中文名为本项目工作音译。",
        "description_en": "This card records the person indexed as Robert Dingley. Chapter 10, p.303, says that in 1735 he wrote to Rosalba Carriera requesting a picture of a young girl in the style of Winter and asking that Smith not be told; Haskell’s account does not establish that Carriera completed it. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp10-p303-dingley-requested-similar-picture"],
        "relation_context_zh": "该请求经Haskell转述自书信；没有依据称Carriera完成了所请求的画作，S2候选留待S6。",
        "relation_context_en": "The request is reported by Haskell from correspondence; there is no evidence here that Carriera completed the requested picture, so the S2 candidate remains for S6.",
        "statement_endpoints": [("st-chp10-p303-dingley-requested-similar-picture", "cand-0921", "cand-9205", "requested_picture_in_style_of_winter_from_carriera_in_1735", "Mr Robert Dingley asked")],
    },
    {
        "candidate": "cand-0979",
        "group": "new-person:charles-errard-5bced1ab85",
        "ku": "units/persons/charles-errard",
        "card": "04-knowledge/units/persons/charles-errard.md",
        "name_zh": "夏尔·埃拉尔",
        "name_en": "Charles Errard",
        "name_field": "索引名",
        "index_entry": "E.csv#14",
        "index_file": "E.csv",
        "index_name": "Errard, Charles",
        "index_page": "106",
        "source_fragments": ["Charles Errard with architectural and landscape backgrounds"],
        "book_sources": [{
            "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
            "source_span": "line 96; print p. 106",
            "location": "第4章第II节 p.106；OCR L96",
            "summary": "Haskell称Charles Errard在版刻前为Poussin绘制的Leonardo笔记插图加上建筑与风景背景，并转述Poussin对这些装饰的批评；S2记录扫描版读作“gauches”，原OCR作“gaufes”。",
            "quote": "embellished by Charles Errard with architectural and landscape backgrounds",
        }],
        "description_zh": "本卡登记索引名为Charles Errard的人物。第4章第II节 p.106称他在版刻前为Poussin绘制的Leonardo笔记插图添加建筑与风景背景；同段转述Poussin的批评，其中原OCR作“gaufes”，S2据扫描校读为“gauches”。该词保留为转述语，不作客观评价。中文名为本项目工作音译。",
        "description_en": "This card records the person indexed as Charles Errard. Chapter 4, section II, p.106, says that he added architectural and landscape backgrounds to Poussin’s illustrations for Leonardo’s notes before engraving. Haskell reports Poussin’s criticism; the OCR reads “gaufes,” while S2 records “gauches” as the scan reading. The term remains attributed speech, not an objective assessment. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp4-sec-ii-l91-99-errard-embellished-drawings-and-poussin-objected"],
        "relation_context_zh": "背景装饰与Poussin的批评均为Haskell转述；“gauches”是被转述的评价，不作客观判断，S2候选留待S6。",
        "relation_context_en": "The embellishment and Poussin’s criticism are reported by Haskell; “gauches” remains an attributed judgment, not an objective assessment. The S2 candidate remains for S6.",
        "statement_endpoints": [("st-chp4-sec-ii-l91-99-errard-embellished-drawings-and-poussin-objected", "cand-0979", "cand-5784", "embellished_drawings_before_engraving", "Charles Errard with architectural and landscape backgrounds")],
    },
    {
        "candidate": "cand-0987",
        "group": "new-person:aniello-falcone-05afc5f58e",
        "ku": "units/persons/aniello-falcone",
        "card": "04-knowledge/units/persons/aniello-falcone.md",
        "name_zh": "阿涅洛·法尔科内",
        "name_en": "Aniello Falcone",
        "name_field": "索引名",
        "index_entry": "F.csv#2",
        "index_file": "F.csv",
        "index_name": "Falcone, Aniello",
        "index_page": "206",
        "source_fragments": ["Aniello Falcone who painted for him a number of lively"],
        "book_sources": [{
            "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
            "source_span": "line 31; print p. 206",
            "location": "第8章 p.206；OCR L31",
            "summary": "Haskell称Roomer特别喜欢Aniello Falcone，并说他为Roomer画了若干生动的战斗场景；“battle scenes without a hero”是描述语，不是已证实的作品题名，数量未说明。",
            "quote": "Aniello Falcone who painted for him a number of lively ‘battle scenes without a hero’",
        }],
        "description_zh": "本卡登记索引名为Aniello Falcone的人物。第8章 p.206称Roomer特别喜欢他，并说他为Roomer绘制了若干生动的战斗场景；“battle scenes without a hero”是描述性短语，不是已证实的作品题名，数量也未明确。中文名为本项目工作音译。",
        "description_en": "This card records the person indexed as Aniello Falcone. Chapter 8, p.206, says Roomer particularly liked him and that he painted a number of lively battle scenes for Roomer. “Battle scenes without a hero” is descriptive wording, not an established title, and the number is unspecified. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp8-p206-falcone-painted-battle-scenes-for-roomer"],
        "relation_context_zh": "Haskell称Falcone为Roomer绘制若干战斗场景；短语并非正式题名，数量不明，S2候选留待S6。",
        "relation_context_en": "Haskell says Falcone painted a number of battle scenes for Roomer; the phrase is not a formal title and the number is unknown. The S2 candidate remains for S6.",
        "statement_endpoints": [("st-chp8-p206-falcone-painted-battle-scenes-for-roomer", "cand-0987", "cand-2223", "artist_painted_war_scenes_for_patron", "Aniello Falcone who painted for him")],
    },
    {
        "candidate": "cand-0994",
        "group": "new-person:cosimo-fanzago-0ba0e98418",
        "ku": "units/persons/cosimo-fanzago",
        "card": "04-knowledge/units/persons/cosimo-fanzago.md",
        "name_zh": "科西莫·范扎戈",
        "name_en": "Cosimo Fanzago",
        "name_field": "索引名",
        "index_entry": "F.csv#9",
        "index_file": "F.csv",
        "index_name": "Fanzago, Cosimo",
        "index_page": "172",
        "source_fragments": ["the local sculptor Cosimo Fanzago"],
        "book_sources": [{
            "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
            "source_span": "line 301; print p. 172",
            "location": "第7章 p.172；OCR L301",
            "summary": "Haskell称Finelli获得更大装饰份额的安排遭到当地雕塑家Cosimo Fanzago强烈反对；“this”指该份额扩大，原文没有说明正式争端或结果。",
            "quote": "the local sculptor Cosimo Fanzago",
        }],
        "description_zh": "本卡登记索引名为Cosimo Fanzago的人物。第7章 p.172称他是当地雕塑家，并说Finelli获得更大装饰份额的安排遭到其强烈反对；原文未说明正式争端或结果。中文名为本项目工作音译。",
        "description_en": "This card records the person indexed as Cosimo Fanzago. Chapter 7, p.172, identifies him as a local sculptor and says that the enlarged share of the decoration for Finelli met with his strong opposition; the passage describes no formal dispute or outcome. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp7-p172-cont-i08"],
        "relation_context_zh": "“this”指Finelli获得更大装饰份额的安排；书中没有交代正式争端或结局，S2候选留待S6。",
        "relation_context_en": "“This” refers to the enlarged share of the decoration assigned to Finelli; the book does not describe a formal dispute or outcome, so the S2 candidate remains for S6.",
        "statement_endpoints": [("st-chp7-p172-cont-i08", "cand-0994", "cand-1038", "fanzago_opposed_finelli_larger_decoration_share", "local sculptor Cosimo Fanzago")],
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Register six source-backed person groups in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = base.sync.read_csv(ALIGNMENT_PATH)
    _, candidates = base.sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = base.sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(candidate_by_id) == len(alignment_by_id)
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    assert len(manifest_by_ku) == len(manifest)
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [
        json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    statement_by_id = {row["statement_id"]: row for row in statements}
    before_stats = base.sync.summarize_by_type(candidates, alignments)

    for t in TARGETS:
        cid = t["candidate"]
        c, a = candidate_by_id[cid], alignment_by_id[cid]
        assert c.get("suggested_type") == "person"
        assert a.get("decision") == "new" and not a.get("ku_id")
        assert base.sync.get_group(a.get("resolution_note", "")) == t["group"]
        assert c.get("index_entry_id") == t["index_entry"]
        assert c.get("canonical_name") == t["index_name"]
        group_members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
            and base.sync.get_group(row.get("resolution_note", "")) == t["group"]
        ]
        assert group_members == [cid], (t["group"], group_members)
        index_row_number = int(t["index_entry"].split("#")[1])
        index_row = base.read_index_rows(t["index_file"])[index_row_number]
        assert index_row.get("Main Entry") == t["index_name"]
        assert index_row.get("Page Numbers", "") == t["index_page"]
        combined_source_text = "\n".join(
            (ROOT / source_file).read_text(encoding="utf-8-sig")
            for source_file in {s["source_file"] for s in t["book_sources"]}
        )
        assert all(fragment in combined_source_text for fragment in t["source_fragments"]), cid
        normalized_source = re.sub(r"\s+", " ", combined_source_text)
        for source in t["book_sources"]:
            assert re.sub(r"\s+", " ", source["quote"]) in normalized_source, (cid, source["source_span"])
        direct = {
            row["statement_id"] for row in statements
            if (row.get("qualifiers") or {}).get("relation_candidate") is True
            and cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
        }
        expected_direct = {row[0] for row in t["statement_endpoints"]}
        assert direct == expected_direct, (cid, direct, expected_direct)
        for sid, subject, obj, predicate, quote_fragment in t["statement_endpoints"]:
            statement = statement_by_id[sid]
            assert statement.get("subject_candidate_id") == subject
            assert statement.get("object_candidate_id") == obj
            assert statement.get("predicate") == predicate
            assert quote_fragment in statement.get("original_quote", ""), (sid, quote_fragment)
        assert t["ku"] not in manifest_by_ku
        assert t["card"] not in accepted_paths
        assert not (ROOT / t["card"]).exists()
        assert not any(
            row.get("type") == "person" and (row.get("name_en") or "").casefold() == t["name_en"].casefold()
            for row in manifest
        )

    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    for t in TARGETS:
        a = next(row for row in planned_alignments if row.get("candidate_id") == t["candidate"] and not row.get("external_source"))
        a["ku_id"] = t["ku"]
        a["process_ref"] = PROCESS_REF
        note = t.get("alignment_note", "书内索引及正文全名支持source-local人物登记，来源限定保留，直接关系候选仍待S6。")
        a["resolution_note"] += f" S4登记（{DATE}）：{t['group']} 映射至 {t['ku']}；{note}"
        planned_manifest.append({
            "ku_id": t["ku"], "type": "person", "canonical_name": t["name_zh"],
            "name_en": t["name_en"], "source_task": TASK, "card_path": t["card"],
        })
    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = accepted_lines
    for t in TARGETS:
        planned_accepted = base.insert_accepted(planned_accepted, t["card"])
    assert len(accepted_paths) + len(TARGETS) == len(
        {line[2:] for line in planned_accepted if line.startswith("- 04-knowledge/units/")}
    )

    stats = base.sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    after_totals = {key: sum(row[key] for row in before_stats.values()) for key in next(iter(before_stats.values()))}
    assert stats["person"]["registered_groups"] == before_stats["person"]["registered_groups"] + len(TARGETS)
    assert stats["person"]["registered_members"] == before_stats["person"]["registered_members"] + len(TARGETS)
    assert totals["registered_groups"] == after_totals["registered_groups"] + len(TARGETS)
    assert totals["registered_members"] == after_totals["registered_members"] + len(TARGETS)
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    cards = {t["card"]: base.make_card(t) for t in TARGETS}
    for card in cards.values():
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert match and isinstance(base.yaml.safe_load(match.group(1)), dict)

    process_text = base.process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    group_lines = []
    for t in TARGETS:
        statement_ids = ", ".join(f"{BT}{sid}{BT}" for sid in t["relation_ids"])
        group_lines.append(
            f"- {BT}{t['candidate']}{BT}（{BT}{t['group']}{BT}）→ "
            f"[{t['name_zh']}（{t['name_en']}）](../../../{t['card']})；"
            f"S2直接关系候选 {statement_ids} 留待S6；{t['relation_context_zh']}"
        )
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物：六组身份组登记（{DATE}）\n\n"
        + "\n".join(group_lines)
        + "\n\n本批登记6个单候选S3 new人物组，每组映射一张KU。姓名结构化字段仅登记索引主项；没有新增外部身份事实或formal relations。"
        "Pietro Paolo Crescenzi的正文身份指代与索引条目的对应仍未确认，故卡片仅登记索引人物并保留S2候选；Curli的书信刊本未独立查阅；"
        "Dingley请求的画作未证明完成；Errard引文保留OCR与扫描校读差异；Falcone场景短语不是已证实题名；Fanzago段落不证明正式争端或结果。\n\n"
        f"登记后人物类型S4为{base.sync.fmt(stats['person']['registered_groups'])}组/"
        f"{base.sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{base.sync.fmt(stats['person']['pending_groups'])}组/{base.sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{base.sync.fmt(totals['registered_groups'])}组/{base.sync.fmt(totals['registered_members'])}条已登记、"
        f"{base.sync.fmt(totals['pending_groups'])}组/{base.sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = base.sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text, count = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{base.sync.fmt(totals['pending_members'])}\g<2>", result_text, count=1,
    )
    assert count == 1
    result_text += (
        f"\n\n### S4人物身份组登记：六个端点（{DATE}）\n\n"
        + "；".join(f"{BT}{t['candidate']}{BT} → {BT}../units/persons/{t['ku'].split('/')[-1]}.md{BT}" for t in TARGETS)
        + "。六组均为单候选S3 new组；索引姓名与书内证据可追溯，身份限定见过程记录。直接关系候选留待S6，本批不创建formal relations。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: six singleton person groups; candidate/index/source/S2 relation checks passed; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; registered="
            f"{totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; person_registered="
            f"{stats['person']['registered_groups']}/{stats['person']['registered_members']}"
        )
        print("formal_relations_added=0; enrichment_rows_changed=0; no files changed")
        return 0

    for rel_path, card in cards.items():
        (ROOT / rel_path).write_text(card, encoding="utf-8", newline="\n")
    base.sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    base.sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups={len(TARGETS)}; candidate_mappings={len(TARGETS)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}; formal_relations_added=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
