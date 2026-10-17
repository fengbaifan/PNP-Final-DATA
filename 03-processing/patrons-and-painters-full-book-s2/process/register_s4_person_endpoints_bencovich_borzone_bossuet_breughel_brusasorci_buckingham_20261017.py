from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_endpoints_assereto_barelli_baretti_bartoli_basadonna_bassi_20261017 as helper  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s4-person-endpoints-bencovich-borzone-bossuet-breughel-brusasorci-buckingham-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BT = chr(96)
helper.DATE = DATE
helper.PROCESS_REF = PROCESS_REF

TARGETS = [
    {
        "candidate": "cand-0286", "members": ["cand-0286"], "group": "new-person:bencovich-federico-1928910f49",
        "ku": "units/persons/federico-bencovich", "card": "04-knowledge/units/persons/federico-bencovich.md",
        "name_zh": "费德里科·本科维奇", "name_en": "Federico Bencovich", "name_field": "索引名",
        "index_entries": [{"entry": "B.csv#133", "file": "B.csv", "name": "Bencovich, Federico", "page": "278"}],
        "source_fragments": ["In 1716 the Dalmatian Federico Bencovich followed them there"],
        "book_sources": [{"source_file": "02-sources/02-Markdown/10_CHP-10_intro.md", "source_span": "line 30; print p. 278", "location": "第10章 p.278；OCR L30", "summary": "Haskell称Dalmatian画家Federico Bencovich于1716年跟随“them”前往Vienna；此句没有明确说明“them”的先行词。注2所引研究未独立查阅。", "quote": "In 1716 the Dalmatian Federico Bencovich followed them there."}],
        "description_zh": "本卡登记Federico Bencovich。第10章 p.278称这位Dalmatian画家于1716年跟随“them”前往Vienna；原文没有明确“them”的先行词，不据此推断其受Hapsburgs雇用或属于某一特定艺术家群体。注2所引研究未独立查阅。中文名为本项目工作音译。",
        "description_en": "This card records Federico Bencovich. Chapter 10, p.278, says that the Dalmatian painter followed “them” to Vienna in 1716; the antecedent of “them” is not clear, so this does not establish employment by the Hapsburgs or membership in a particular artist group. The study cited in note 2 was not independently consulted. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp10-p278-bencovich-followed-to-vienna"],
        "relation_context_zh": "“there”指Vienna；“them”的复数先行词未确定，不推断雇用关系或群体归属，S2候选留待S6。",
        "relation_context_en": "“There” refers to Vienna; the plural antecedent of “them” is unresolved, and no employment or group membership is inferred. The S2 candidate remains for S6.",
        "statement_endpoints": [("st-chp10-p278-bencovich-followed-to-vienna", "cand-0286", "cand-2772", "bencovich_followed_them_to_vienna_in_1716", "followed them there")],
    },
    {
        "candidate": "cand-0410", "members": ["cand-0410"], "group": "new-person:borzone-francesco-26c9abc1e6",
        "ku": "units/persons/francesco-borzone", "card": "04-knowledge/units/persons/francesco-borzone.md",
        "name_zh": "弗朗切斯科·博尔佐内", "name_en": "Francesco Borzone", "name_field": "索引名",
        "index_entries": [{"entry": "B.csv#257", "file": "B.csv", "name": "Borzone, Francesco", "page": "189"}],
        "source_fragments": ["Francesco Borzone who had been summoned to Paris at the beginning of the new reign", "employed by the King until 1679"],
        "book_sources": [{"source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md", "source_span": "line 246; print p. 189", "location": "第7章 p.189；OCR L246", "summary": "Haskell称Francesco Borzone在新王朝初年受召前往Paris，并受国王雇用至1679年；原文没有据此给“新王朝初年”定出更精确年份。注1所引Soprani未独立查阅。", "quote": "Francesco Borzone who had been summoned to Paris at the beginning of the new reign was generously employed by the King until 1679."}],
        "description_zh": "本卡登记Francesco Borzone。第7章 p.189称他在新王朝初年受召前往Paris，并受国王雇用至1679年；Haskell没有将“新王朝初年”精确到某一年。注1所引Soprani未独立查阅。中文名为本项目工作音译。",
        "description_en": "This card records Francesco Borzone. Chapter 7, p.189, says that he was summoned to Paris at the beginning of the new reign and was employed by the King until 1679; Haskell does not assign an exact year to the beginning of that reign. The Soprani reference in note 1 was not independently consulted. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp7-p189-i05"],
        "relation_context_zh": "“新王朝初年”保留原文宽泛时间范围；受雇记录为Haskell转述并引Soprani，候选留待S6。",
        "relation_context_en": "The broad timing “beginning of the new reign” is retained; the employment statement is Haskell’s account citing Soprani, and the candidate remains for S6.",
        "statement_endpoints": [("st-chp7-p189-i05", "cand-1447", "cand-0410", "employed_francesco_borzone_until_1679", "Francesco Borzone who had been summoned to Paris")],
    },
    {
        "candidate": "cand-0415", "members": ["cand-0415"], "group": "new-person:benigne-bossuet-jacques-a6e63d1549",
        "ku": "units/persons/jacques-benigne-bossuet", "card": "04-knowledge/units/persons/jacques-benigne-bossuet.md",
        "name_zh": "雅克-贝尼涅·博须埃", "name_en": "Jacques-Bénigne Bossuet", "name_field": "索引名",
        "index_entries": [{"entry": "B.csv#262", "file": "B.csv", "name": "Bossuet, Jacques-Bénigne", "page": "334, 335"}],
        "source_fragments": ["The revived interest in Bossuet at this time was directly concerned with the increasing spread of heretical opinions throughout Europe"],
        "book_sources": [{"source_file": "02-sources/02-Markdown/13_CHP-13_intro.md", "source_span": "line 29; print p. 334", "location": "第13章 p.334；OCR L29", "summary": "Haskell将此时对Bossuet的重新关注与异端观点在欧洲扩散联系起来；这是作者的历史解释，不是独立核实的事实。正文只写Bossuet姓氏，全名来自索引。", "quote": "The revived interest in Bossuet at this time was directly concerned with the increasing spread of heretical opinions throughout Europe"}],
        "description_zh": "本卡登记索引所列Jacques-Bénigne Bossuet。第13章 p.334称此时对Bossuet的重新关注与异端观点在欧洲扩散相关；这是Haskell的历史解释，未独立核实。正文仅用Bossuet姓氏，全名来自索引。中文名为本项目工作音译。",
        "description_en": "This card records the person indexed as Jacques-Bénigne Bossuet. Chapter 13, p.334, links renewed interest in Bossuet at the time to the spread of heretical opinions in Europe; this is Haskell’s historical interpretation and was not independently verified. The body uses only the surname; the full name comes from the index. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp13-p334-bossuet-interest-and-heresy-context"],
        "relation_context_zh": "该关联为Haskell对书籍出版背景的历史解释，不作独立事实核验，S2候选留待S6。",
        "relation_context_en": "This is Haskell’s historical interpretation of the publishing context, not an independently verified fact; the S2 candidate remains for S6.",
        "statement_endpoints": [("st-chp13-p334-bossuet-interest-and-heresy-context", "cand-0415", "cand-12132", "renewed_interest_in_bossuet_linked_to_spread_of_heresy", "revived interest in Bossuet")],
    },
    {
        "candidate": "cand-0448", "members": ["cand-0448"], "group": "new-person:abram-breughel-becae77cfc",
        "ku": "units/persons/abram-breughel", "card": "04-knowledge/units/persons/abram-breughel.md",
        "name_zh": "阿布拉姆·勃鲁盖尔", "name_en": "Abram Breughel", "name_field": "索引名",
        "index_entries": [{"entry": "B.csv#295", "file": "B.csv", "name": "Breughel, Abram", "page": "210"}],
        "source_fragments": ["Flemish agent in Rome Abram Breughel was probably not being insincere", "pictures of Rembrandt are not very highly thought of here"],
        "book_sources": [{"source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md", "source_span": "line 74; print p. 210", "location": "第8章第I节 p.210；OCR L74", "summary": "Haskell称Abram Breughel是Russo在Rome的Flemish代理人，并转述他1665年写信称Rembrandt绘画在“here”并不受高度评价；信件未独立查阅，here所指范围未确定。", "quote": "Flemish agent in Rome Abram Breughel was probably not being insincere (as has been suggested) when he wrote in 1665 that ‘the pictures of Rembrandt are not very highly thought of here’"}],
        "description_zh": "本卡登记Abram Breughel。第8章第I节 p.210称他是Russo在Rome的Flemish代理人，并转述他1665年写信称Rembrandt的画在“here”并不受高度评价。Haskell称其大概并非虚伪；原信未独立查阅，here的地理范围未确定。中文名为本项目工作音译。",
        "description_en": "This card records Abram Breughel. Chapter 8, section I, p.210, identifies him as Russo’s Flemish agent in Rome and reports that in a 1665 letter he wrote that Rembrandt’s pictures were not highly regarded “here.” Haskell says he was probably not insincere; the letter was not independently consulted, and the geographic scope of “here” remains undefined. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp8-p210-breughel-reported-rembrandt-reception-1665"],
        "relation_context_zh": "对Rembrandt绘画评价为Haskell转述Breughel的书信；“here”范围未定，Haskell关于其并非虚伪亦是作者判断，S2候选留待S6。",
        "relation_context_en": "The comment on Rembrandt’s pictures is Haskell’s report of Breughel’s letter; “here” is undefined, and Haskell’s view that Breughel was sincere is the author’s judgment. The S2 candidate remains for S6.",
        "statement_endpoints": [("st-chp8-p210-breughel-reported-rembrandt-reception-1665", "cand-0448", "cand-12040", "breughel_reported_low_regard_for_rembrandt_pictures_in_1665", "Abram Breughel was probably not being insincere")],
    },
    {
        "candidate": "cand-0460", "members": ["cand-0460"], "group": "new-person:brusasorci-felice-7846e65690",
        "ku": "units/persons/felice-brusasorci", "card": "04-knowledge/units/persons/felice-brusasorci.md",
        "name_zh": "费利切·布鲁萨索尔奇", "name_en": "Felice Brusasorci", "name_field": "索引名",
        "index_entries": [{"entry": "B.csv#307", "file": "B.csv", "name": "Brusasorci, Felice", "page": "216"}],
        "source_fragments": ["a Capuchin pupil of the\nVeronese Brusasorci, Padre Massimo"],
        "book_sources": [{"source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md", "source_span": "lines 29-31; print p. 216", "location": "第8章第II节 p.216；OCR L29-31", "summary": "Haskell称Padre Massimo是Veronese Brusasorci的Capuchin学生；原文没有给训练时间或地点。“Veronese”仅保留为地域形容词，不推断出生地或居住地。正文只用姓氏，全名来自索引。", "quote": "a Capuchin pupil of the\nVeronese Brusasorci, Padre Massimo"}],
        "description_zh": "本卡登记索引名为Felice Brusasorci的人物。第8章第II节 p.216称Padre Massimo是Brusasorci的Capuchin学生，并以Veronese修饰其姓氏；原文没有训练时间或地点，也不能由该形容词推断出生地或居住地。中文名为本项目工作音译。",
        "description_en": "This card records the person indexed as Felice Brusasorci. Chapter 8, section II, p.216, calls Padre Massimo a Capuchin pupil of Brusasorci and uses “Veronese” as a regional adjective; it supplies no date or place of training, and the adjective does not establish birthplace or residence. The full name comes from the index. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp8-p216-massimo-pupil-of-brusasorci", "st-chp8-p216-brusasorci-described-as-veronese"],
        "relation_context_zh": "师生说按Haskell书内叙述保留，不补入训练地点或日期；Veronese不转换为出生地/居住地事实。两项S2候选留待S6。",
        "relation_context_en": "The teacher-pupil statement is retained as Haskell’s account without adding a training place or date; “Veronese” is not converted into a birthplace or residence claim. Both S2 candidates remain for S6.",
        "statement_endpoints": [
            ("st-chp8-p216-massimo-pupil-of-brusasorci", "cand-1576", "cand-0460", "pupil_of", "pupil of the Veronese Brusasorci"),
            ("st-chp8-p216-brusasorci-described-as-veronese", "cand-0460", "cand-7661", "described_as_veronese", "Veronese Brusasorci"),
        ],
    },
    {
        "candidate": "cand-0464", "members": ["cand-0464"], "group": "new-person:buckingham-charles-of-villiers-25a2484d8a",
        "ku": "units/persons/charles-villiers-duke-of-buckingham", "card": "04-knowledge/units/persons/charles-villiers-duke-of-buckingham.md",
        "name_zh": "查尔斯·维利尔斯（白金汉公爵）", "name_en": "Charles Villiers, Duke of Buckingham", "name_field": "索引名",
        "index_entries": [{"entry": "B.csv#312", "file": "B.csv", "name": "Buckingham, Charles Villiers, Duke of", "page": "178"}],
        "source_fragments": ["enthusiastically welcomed by Charles and the Duke of Buckingham"],
        "book_sources": [{"source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md", "source_span": "line 106; print p. 178", "location": "第7章 p.178；OCR L106", "summary": "Haskell称Orazio Gentileschi在England受到Charles与Duke of Buckingham热情欢迎；正文只用公爵头衔，完整索引名为Charles Villiers。该句未说明两人中谁发起欢迎。", "quote": "In England, where he was enthusiastically welcomed by Charles and the Duke of Buckingham, this process was carried still further"}],
        "description_zh": "本卡登记索引名为Charles Villiers, Duke of Buckingham的人物。第7章 p.178称Orazio Gentileschi在England受到Charles与白金汉公爵热情欢迎；正文只用公爵头衔，完整姓名来自同页索引。该句没有说明两名赞助者中谁发起欢迎。中文名为本项目工作音译。",
        "description_en": "This card records the person indexed as Charles Villiers, Duke of Buckingham. Chapter 7, p.178, says Orazio Gentileschi was enthusiastically welcomed in England by Charles and the Duke of Buckingham; the body uses the ducal title, while the full name comes from the same-page index. It does not say which of the two patrons initiated the welcome. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp7-p178-i10"],
        "relation_context_zh": "Haskell将Charles与白金汉公爵并列为欢迎者，但不指定具体发起者；完整姓名由同页索引提供，S2候选留待S6。",
        "relation_context_en": "Haskell lists Charles and the Duke of Buckingham as welcoming Gentileschi but does not specify who initiated the welcome; the full name comes from the same-page index. The S2 candidate remains for S6.",
        "statement_endpoints": [("st-chp7-p178-i10", "cand-1135", "cand-0464", "welcomed_in_england_and_style_developed_further", "welcomed by Charles and the Duke of Buckingham")],
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Register six source-backed new person groups in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    base = helper.base
    alignment_fields, alignments = base.sync.read_csv(ALIGNMENT_PATH)
    _, candidates = base.sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = base.sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    assert len(candidate_by_id) == len(alignment_by_id) and len(manifest_by_ku) == len(manifest)
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}
    before_stats = base.sync.summarize_by_type(candidates, alignments)

    for t in TARGETS:
        member_ids = t["members"]
        for cid in member_ids:
            c, a = candidate_by_id[cid], alignment_by_id[cid]
            assert c.get("suggested_type") == "person"
            assert a.get("decision") == "new" and not a.get("ku_id")
            assert base.sync.get_group(a.get("resolution_note", "")) == t["group"]
        group_members = [row["candidate_id"] for row in alignments if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new" and base.sync.get_group(row.get("resolution_note", "")) == t["group"]]
        assert set(group_members) == set(member_ids), (t["group"], group_members)
        for entry in t["index_entries"]:
            index_row = base.read_index_rows(entry["file"])[int(entry["entry"].split("#")[1])]
            assert index_row.get("Main Entry") == entry["name"] and index_row.get("Page Numbers", "") == entry["page"]
        combined_source_text = "\n".join((ROOT / file).read_text(encoding="utf-8-sig") for file in {s["source_file"] for s in t["book_sources"]})
        normalized_source = re.sub(r"\s+", " ", combined_source_text)
        assert all(re.sub(r"\s+", " ", fragment) in normalized_source for fragment in t["source_fragments"]), t["candidate"]
        for source in t["book_sources"]:
            assert re.sub(r"\s+", " ", source["quote"]) in normalized_source, (t["candidate"], source["source_span"])
        direct = {row["statement_id"] for row in statements if (row.get("qualifiers") or {}).get("relation_candidate") is True and (row.get("subject_candidate_id") in member_ids or row.get("object_candidate_id") in member_ids)}
        expected_direct = {row[0] for row in t["statement_endpoints"]}
        assert direct == expected_direct, (t["group"], direct, expected_direct)
        for sid, subject, obj, predicate, quote_fragment in t["statement_endpoints"]:
            statement = statement_by_id[sid]
            normalized_quote = re.sub(r"\s+", " ", statement.get("original_quote", ""))
            assert statement.get("subject_candidate_id") == subject and statement.get("object_candidate_id") == obj
            assert statement.get("predicate") == predicate and re.sub(r"\s+", " ", quote_fragment) in normalized_quote, sid
        assert t["ku"] not in manifest_by_ku and t["card"] not in accepted_paths and not (ROOT / t["card"]).exists()
        assert not any(row.get("type") == "person" and (row.get("name_en") or "").casefold() == t["name_en"].casefold() for row in manifest)

    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    for t in TARGETS:
        for cid in t["members"]:
            a = next(row for row in planned_alignments if row.get("candidate_id") == cid and not row.get("external_source"))
            a["ku_id"] = t["ku"]
            a["process_ref"] = PROCESS_REF
            a["resolution_note"] += f" S4登记（{DATE}）：{t['group']} 映射至 {t['ku']}；书内索引与正文支持source-local人物登记，来源限定保留，直接关系候选留待S6。"
        planned_manifest.append({"ku_id": t["ku"], "type": "person", "canonical_name": t["name_zh"], "name_en": t["name_en"], "source_task": TASK, "card_path": t["card"]})
    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = accepted_lines
    for t in TARGETS:
        planned_accepted = base.insert_accepted(planned_accepted, t["card"])
    assert len(accepted_paths) + len(TARGETS) == len({line[2:] for line in planned_accepted if line.startswith("- 04-knowledge/units/")})

    stats = base.sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(row[key] for row in before_stats.values()) for key in next(iter(before_stats.values()))}
    assert stats["person"]["registered_groups"] == before_stats["person"]["registered_groups"] + len(TARGETS)
    assert stats["person"]["registered_members"] == before_stats["person"]["registered_members"] + len(TARGETS)
    assert totals["registered_groups"] == before_totals["registered_groups"] + len(TARGETS)
    assert totals["registered_members"] == before_totals["registered_members"] + len(TARGETS)
    assert totals["pending_groups"] == before_totals["pending_groups"] - len(TARGETS)
    assert totals["pending_members"] == before_totals["pending_members"] - len(TARGETS)
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    cards = {t["card"]: helper.make_card(t) for t in TARGETS}
    for card in cards.values():
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert match and isinstance(base.yaml.safe_load(match.group(1)), dict)
    process_text = base.process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    group_lines = []
    for t in TARGETS:
        relation_labels = ", ".join(f"{BT}{sid}{BT}" for sid in t["relation_ids"])
        group_lines.append(f"- {BT}{t['candidate']}{BT}（{BT}{t['group']}{BT}）→ [{t['name_zh']}（{t['name_en']}）](../../../{t['card']})；S2直接关系候选 {relation_labels} 留待S6；{t['relation_context_zh']}")
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物：六组直接关系端点登记（{DATE}）\n\n"
        + "\n".join(group_lines)
        + "\n\n本批登记6个单候选S3 new人物组，每组映射一张KU。人物全名以正文或同页索引为锚；Bencovich指代、Borzone年代、Bossuet历史解释、"
        "Breughel引文范围、Brusasorci地域修饰与Buckingham公爵姓名来源均保留限定。本批不添加外部身份事实或formal relations。\n\n"
        f"登记后人物类型S4为{base.sync.fmt(stats['person']['registered_groups'])}组/{base.sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{base.sync.fmt(stats['person']['pending_groups'])}组/{base.sync.fmt(stats['person']['pending_members'])}条待登记；全书为"
        f"{base.sync.fmt(totals['registered_groups'])}组/{base.sync.fmt(totals['registered_members'])}条已登记、"
        f"{base.sync.fmt(totals['pending_groups'])}组/{base.sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = base.sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text, count = re.subn(r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)", rf"\g<1>{base.sync.fmt(totals['pending_members'])}\g<2>", result_text, count=1)
    assert count == 1
    enrichment_rows = sum(1 for line in ENRICHMENT_PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip()) + len(TARGETS)
    result_lines = result_text.splitlines()
    enrichment_indexes = [i for i, line in enumerate(result_lines) if line.startswith("| [既有字段表]")]
    assert len(enrichment_indexes) == 1
    result_lines[enrichment_indexes[0]] = f"| [既有字段表](../tables/enrichment.jsonl) | {base.sync.fmt(enrichment_rows)}条，其中1,615条 unverified |"
    result_text = "\n".join(result_lines)
    result_text += (
        f"\n\n### S4人物身份组登记：六个直接关系端点（{DATE}）\n\n"
        + "；".join(f"{BT}{t['candidate']}{BT} → {BT}../units/persons/{t['ku'].split('/')[-1]}.md{BT}" for t in TARGETS)
        + "。六组均为单候选S3 new组；直接关系候选留待S6，本批不创建formal relations。"
    )

    if args.dry_run:
        print(f"dry-run passed: groups=6; mappings=6; index/source/S2 relation checks passed; manifest={len(manifest)}->{len(planned_manifest)}; registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; enrichment={enrichment_rows}; formal_relations_added=0; no files changed")
        return 0

    for rel_path, card in cards.items():
        (ROOT / rel_path).write_text(card, encoding="utf-8", newline="\n")
    base.sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    base.sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: groups=6; mappings=6; registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; formal_relations_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
