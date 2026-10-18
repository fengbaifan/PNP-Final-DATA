from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402
from scripts.build_field_facts import assign_ids, extract_records  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
DATE = "2026-10-18"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
SOURCES_PATH = TABLES / "sources.csv"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ANCHOR = "s3-s4-person-m-index-endpoints-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index, M.csv."

DB_MAX_URL = "https://www.deutsche-biographie.de/gnd11857941X.html"
DB_MAUPERTUIS_URL = "https://www.deutsche-biographie.de/gnd118731998.html?language=en"
DB_CHRISTIAN_URL = "https://www.deutsche-biographie.de/gnd102111847.html"
NPG_SARAH_URL = "https://www.npg.org.uk/collections/search/person/mp02960/sarah-churchill-nee-jenyns-jennings-duchess-of-marlborough?wPage=1"
MAX_GROUP = "new-person:maximilian-ii-emanuel-of-bavaria-" + __import__("hashlib").sha256(b"maximilian-ii-emanuel-of-bavaria").hexdigest()[:10]


def book_source(location, summary, file, span, quotes):
    return {
        "citation": BOOK,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": qspan, "text": quote} for qspan, quote in quotes],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": file, "source_span": "; ".join(qspan for qspan, _ in quotes)},
    }


def external_source(citation, url, location, summary, quotes):
    return {
        "citation": citation,
        "url": url,
        "accessed_date": DATE,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": text} for span, text in quotes],
        "evidence_ref": {"source_url": url, "source_span": location},
    }


def chapter(file, location, summary, quotes):
    return (file, location, summary, quotes)


TARGETS = [
    {
        "candidate": "cand-1552", "initial_group": "new-person:duchess-marlborough-of-a578c57838",
        "group": "new-person:sarah-churchill-duchess-of-marlborough", "ku": "units/persons/sarah-churchill",
        "card": "04-knowledge/units/persons/sarah-churchill.md", "name_zh": "萨拉·丘吉尔", "name_en": "Sarah Churchill",
        "indexes": [("M.csv#91", "Marlborough, Duchess of", "278")],
        "chapters": [chapter("02-sources/02-Markdown/10_CHP-10_intro.md", "第10章，印刷页278；OCR L36–39", "Haskell称“Duchess of Marlborough”致信Lord Manchester，并引述其对英国音乐的评论；信件在本书中未标日期。", [("lines 36–39; print p. 278", "‘Music’, wrote the Duchess of Marlborough to Lord Manchester,6")])],
        "external_source": "National Portrait Gallery", "external_id": NPG_SARAH_URL,
        "external_citation": f"National Portrait Gallery, ‘Sarah Churchill (née Jenyns (Jennings)), Duchess of Marlborough’, person record mp02960. {NPG_SARAH_URL} Accessed {DATE}.",
        "external_location": "Person record mp02960, heading and biographical entry, lines 61–68.",
        "external_summary": "NPG将Sarah Churchill（née Jenyns/Jennings）列为Marlborough公爵夫人（1660–1744），并记为John Churchill第一代Marlborough公爵之妻；该身份与Haskell第10章的称谓及Lord Manchester语境相合。",
        "external_quotes": [("lines 61–67", "Sarah Churchill (née Jenyns (Jennings)), Duchess of Marlborough; (1660-1744); The wife of John Churchill, 1st Duke of Marlborough")],
        "name_rows": [("索引称谓", "Marlborough, Duchess of", "S1"), ("正文称谓", "the Duchess of Marlborough", "S2"), ("规范姓名及头衔", "Sarah Churchill (née Jenyns (Jennings)), Duchess of Marlborough", "S3")],
        "description_zh": "本卡登记索引“Marlborough, Duchess of”所指人物。第10章p.278称Marlborough公爵夫人写信给Lord Manchester；同段说明Manchester曾于1709年出使威尼斯。National Portrait Gallery的mp02960记录将Sarah Churchill（née Jenyns/Jennings）列为Marlborough公爵夫人，身份与书内语境相合。书中未给这封信的日期；关于音乐评论的关系候选仍待S6审查。中文名为项目工作音译。",
        "description_en": "This card records the person indexed as “Marlborough, Duchess of.” Chapter 10, p. 278, says the Duchess of Marlborough wrote to Lord Manchester; the same passage notes Manchester's 1709 embassy to Venice. The National Portrait Gallery's record mp02960 identifies Sarah Churchill (née Jenyns/Jennings) as Duchess of Marlborough, matching the book's context. Haskell does not date the letter, and the statement about the music commentary remains for S6 review. The Chinese display name is a project working transliteration.",
        "context_zh": "第10章p.278引述公爵夫人写给Lord Manchester的音乐评论；书中没有给信件日期，原始关系陈述留待S6。",
        "context_en": "Chapter 10, p. 278, quotes a music commentary in a letter from the Duchess to Lord Manchester. The book gives no letter date; the source statement remains for S6.",
        "relations": ["st-chp10-p278-duchess-wrote-manchester-music-letter"],
        "external_note": "Identity comparison only: NPG person record mp02960 identifies Sarah Churchill (née Jenyns/Jennings), 1660–1744, as Duchess of Marlborough and wife of John Churchill, 1st Duke. This matches Haskell's indexed title and the p. 278 context around Lord Manchester's 1709 Venice embassy. Haskell does not date the quoted letter; this alignment does not independently validate its wording or authorship.",
        "s3_note": "NPG person record mp02960 identifies Sarah Churchill (née Jenyns/Jennings), 1660–1744, as Duchess of Marlborough and wife of John Churchill, 1st Duke; Haskell p.278 places the title in the context of Lord Manchester's 1709 Venice embassy. No matching person KU exists. New identity group; the undated letter's attribution is not independently verified and its relation_candidate remains for S6.",
    },
    {
        "candidate": "cand-1585", "initial_group": "new-person:louis-maupertuis-pierre-bddd1f3354",
        "group": "new-person:pierre-louis-moreau-de-maupertuis", "ku": "units/persons/pierre-louis-moreau-de-maupertuis",
        "card": "04-knowledge/units/persons/pierre-louis-moreau-de-maupertuis.md", "name_zh": "皮埃尔-路易·莫罗·德·莫佩尔蒂", "name_en": "Pierre-Louis Moreau de Maupertuis",
        "indexes": [("M.csv#124", "Maupertuis, Pierre-Louis", "349")],
        "chapters": [chapter("02-sources/02-Markdown/14_CHP-14_intro.md", "第14章，印刷页349；OCR L24", "Haskell称Algarotti在巴黎居留時曾遇到Maupertuis；原文没有把随后在Cirey的居住归于Maupertuis。", [("line 24; print p. 349", "he met Pierre Crozat, Maupertuis and Voltaire")])],
        "external_source": "Deutsche Biographie", "external_id": "118731998", "external_url": DB_MAUPERTUIS_URL,
        "external_citation": f"Deutsche Biographie, ‘Maupertuis, Pierre-Louis Moreau de’, GND 118731998. {DB_MAUPERTUIS_URL} Accessed {DATE}.",
        "external_location": "GND 118731998, heading and alternate names, lines 27–56.",
        "external_summary": "Deutsche Biographie的规范记录以Pierre-Louis Moreau de Maupertuis为名，并将“Maupertuis, Pierre-Louis”及“Maupertuis”列为异名；这与索引和正文形式相合。",
        "external_quotes": [("lines 27, 42–48, 56", "Maupertuis, Pierre-Louis Moreau de; Maupertuis, Pierre-Louis; Maupertuis")],
        "name_rows": [("索引姓名", "Maupertuis, Pierre-Louis", "S1"), ("正文姓名", "Maupertuis", "S2"), ("规范姓名", "Pierre-Louis Moreau de Maupertuis", "S3")],
        "description_zh": "本卡登记索引“Maupertuis, Pierre-Louis”及第14章p.349所称Maupertuis。Deutsche Biographie的GND 118731998记录以Pierre-Louis Moreau de Maupertuis为规范名，并列出索引与正文中的两种称名。第14章称Algarotti在巴黎遇见Maupertuis；句中“with whom he stayed at Cirey”指向Voltaire，不扩写为Maupertuis的住宿关系。中文名为项目工作音译。",
        "description_en": "This card records the person indexed as “Maupertuis, Pierre-Louis” and referred to as Maupertuis on p. 349. Deutsche Biographie's GND 118731998 gives Pierre-Louis Moreau de Maupertuis as the heading and lists both book forms as alternate names. Chapter 14 says Algarotti met Maupertuis in Paris; the clause “with whom he stayed at Cirey” refers to Voltaire and is not extended to Maupertuis. The Chinese display name is a project working transliteration.",
        "context_zh": "第14章p.349称Algarotti在巴黎遇见Maupertuis；met关系候选留待S6。",
        "context_en": "Chapter 14, p. 349, says Algarotti met Maupertuis in Paris; the met statement remains for S6.",
        "relations": ["st-chp14-p349-met-maupertuis"],
        "external_note": "Identity comparison only: Deutsche Biographie GND 118731998 gives Pierre-Louis Moreau de Maupertuis as the heading and lists both “Maupertuis, Pierre-Louis” and “Maupertuis” as alternate names. These match Haskell's index M.csv#124 and ch. 14 p. 349. No matching person KU exists; the external record does not validate the book's meeting claim.",
        "s3_note": "Deutsche Biographie GND 118731998 lists “Maupertuis, Pierre-Louis” and “Maupertuis” as names for Pierre-Louis Moreau de Maupertuis, matching the index and p.349 body mention. No matching person KU exists. New identity group; external identity evidence does not validate the meeting claim in the relation_candidate.",
    },
    {
        "candidate": "cand-1586", "initial_group": "new-person:bavaria-elector-emmanuel-max-of-185c8d9fb9",
        "group": MAX_GROUP, "ku": "units/persons/maximilian-ii-emanuel-of-bavaria",
        "card": "04-knowledge/units/persons/maximilian-ii-emanuel-of-bavaria.md", "name_zh": "马克西米连二世·埃曼努埃尔", "name_en": "Maximilian II Emanuel of Bavaria",
        "indexes": [("M.csv#125", "Max Emmanuel, Elector of Bavaria", "193, 278"), ("M.csv#126", "Maximilian, Prince, Elector of Bavaria", "277")],
        "chapters": [
            chapter("02-sources/02-Markdown/07_CHP-7_sec_iv.md", "第7章第IV节，印刷页193；OCR L17", "Haskell称新任巴伐利亚选帝侯Max Emmanuel委托Zuccalli营建Schleissheim。", [("line 17; print p. 193", "under the new Elector Max Emmanuel")]),
            chapter("02-sources/02-Markdown/10_CHP-10_intro.md", "第10章，印刷页277；OCR L16", "Haskell称Maximilian of Bavaria于1704年委托Rosalba绘制其肖像及威尼斯女性肖像。", [("line 16; print p. 277", "Maximilian of Bavaria")]),
            chapter("02-sources/02-Markdown/10_CHP-10_intro.md", "第10章，印刷页278；OCR L31–32", "Haskell称Amigoni在慕尼黑为Elector Max Emmanuel作画。", [("lines 31–32; print p. 278", "painting for the Elector Max Emmanuel")]),
        ],
        "external_source": "Deutsche Biographie", "external_id": "11857941X", "external_url": DB_MAX_URL,
        "external_citation": f"Deutsche Biographie, ‘Maximilian II. Emanuel’, GND 11857941X. {DB_MAX_URL} Accessed {DATE}.",
        "external_location": "GND 11857941X, alternate names and entry, lines 76–89, 240–242.",
        "external_summary": "Deutsche Biographie列出Max Emanuel、Maximilian Emanuel及Maximilian II. Emanuel等异名，并记其自1679年为巴伐利亚选帝侯，生于1662年；这将cand-1586与cand-1587指向同一人物。",
        "external_quotes": [("lines 76–88", "Max Emanuel; Maximilian II. Emanuel, Elector of Bavaria"), ("lines 240–242", "Kurfürst von Bayern (seit 1679); geboren 11.7.1662")],
        "name_rows": [("索引姓名", "Max Emmanuel, Elector of Bavaria", "S1"), ("索引姓名异项", "Maximilian, Prince, Elector of Bavaria", "S2"), ("正文称名", "Maximilian of Bavaria", "S4"), ("正文称名异体", "Elector Max Emmanuel", "S5"), ("规范姓名", "Maximilian II. Emanuel, Elector of Bavaria", "S6")],
        "description_zh": "本卡将cand-1586（索引M.csv#125）与cand-1587（索引M.csv#126）归为同一人物组。Haskell第7章p.193和第10章p.278称Elector Max Emmanuel，第10章p.277称Maximilian of Bavaria并记其1704年委托；Deutsche Biographie GND 11857941X将Max Emanuel与Maximilian II. Emanuel列为同一规范记录的称名，且记其自1679年为巴伐利亚选帝侯。项目中没有既有同一人物KU，故登记一张卡并承接两条候选映射。中文名为项目工作音译。",
        "description_en": "This card groups cand-1586 (index M.csv#125) and cand-1587 (index M.csv#126) as one person. Haskell uses “Elector Max Emmanuel” on p. 193 and p. 278, and “Maximilian of Bavaria” on p. 277 for the 1704 commission. Deutsche Biographie GND 11857941X lists Max Emanuel and Maximilian II. Emanuel under one authority record and records him as Elector of Bavaria from 1679. No matching person KU exists in the project, so one card receives both candidate mappings. The Chinese display name is a project working transliteration.",
        "context_zh": "第10章p.277的肖像委托及p.278的Amigoni作画陈述各保留为S2关系候选，留待S6；本轮不写正式边。",
        "context_en": "The p. 277 portrait commission and p. 278 statement about Amigoni remain separate S2 relation candidates for S6; no formal edge is created here.",
        "relations": ["st-chp10-p277-maximilian-carriera-portrait-commissions", "st-chp10-p278-amigoni-max_emmanuel"],
        "external_note": "Identity comparison only: Deutsche Biographie GND 11857941X lists Max Emanuel, Maximilian Emanuel, and Maximilian II. Emanuel among the names for one elector; it records the Elector of Bavaria from 1679, born in 1662. The authority record matches the chapter 7 p. 193 and chapter 10 pp. 277–278 forms, establishing cand-1586 and cand-1587 as one source-local identity group. No book claims are independently validated by this name alignment.",
        "s3_note": "Deutsche Biographie GND 11857941X lists Max Emanuel and Maximilian II. Emanuel under one identity and records him as Elector of Bavaria from 1679. This matches cand-1586 (pp.193, 278) and cand-1587 (p.277, commission in 1704). The prior separate groups are superseded and merged as one new identity group; no matching person KU exists.",
    },
    {
        "candidate": "cand-1605", "initial_group": "new-person:christian-louis-mecklenburg-of-6ce0779819",
        "group": "new-person:christian-ludwig-ii-mecklenburg-schwerin", "ku": "units/persons/christian-ludwig-ii-of-mecklenburg-schwerin",
        "card": "04-knowledge/units/persons/christian-ludwig-ii-of-mecklenburg-schwerin.md", "name_zh": "克里斯蒂安·路德维希二世", "name_en": "Christian Ludwig II of Mecklenburg-Schwerin",
        "indexes": [("M.csv#145", "Mecklenburg, Christian Louis, Duke of", "277")],
        "chapters": [chapter("02-sources/02-Markdown/10_CHP-10_intro.md", "第10章，印刷页277；OCR L16–18", "Haskell称Duke Christian Louis of Mecklenburg随后作出类似委托并邀请Rosalba前往德国；原OCR在Mecklenburg处换行。", [("lines 16–18; print p. 277", "He was followed by Duke Christian Louis of Mecklenburg")])],
        "external_source": "Deutsche Biographie", "external_id": "102111847", "external_url": DB_CHRISTIAN_URL,
        "external_citation": f"Deutsche Biographie, ‘Christian Ludwig II’, GND 102111847. {DB_CHRISTIAN_URL} Accessed {DATE}.",
        "external_location": "GND 102111847, heading, alternate names, and dates, lines 26–50, 180–193.",
        "external_summary": "Deutsche Biographie以Christian Ludwig II von Mecklenburg-Schwerin为规范身份，并列“Christian Ludwig, Mecklenburg, Herzog”为异名，生卒为1683–1756；Haskell索引的Christian Louis公爵形式相合。",
        "external_quotes": [("lines 26–50", "Christian Ludwig II von Mecklenburg-Schwerin; Christian Ludwig, Mecklenburg, Herzog"), ("lines 180–182", "Herzog von Mecklenburg-Schwerin; geboren 18.5.1683; gestorben 30.5.1756")],
        "name_rows": [("索引姓名", "Mecklenburg, Christian Louis, Duke of", "S1"), ("正文姓名", "Duke Christian Louis of Mecklenburg", "S2"), ("规范姓名", "Christian Ludwig II of Mecklenburg-Schwerin", "S3")],
        "description_zh": "本卡登记索引M.csv#145及第10章p.277中的Christian Louis of Mecklenburg。Deutsche Biographie GND 102111847以Christian Ludwig II von Mecklenburg-Schwerin为规范身份，并列出与Haskell相同的“Christian Ludwig, Mecklenburg, Herzog”称名及1683–1756年生卒。原文称其在Maximilian之后作出类似委托，但没有给出该委托日期；本卡只据姓名与头衔对齐，不新增履历事实。中文名为项目工作音译。",
        "description_en": "This card records the Christian Louis of Mecklenburg indexed at M.csv#145 and named on p. 277. Deutsche Biographie GND 102111847 gives Christian Ludwig II of Mecklenburg-Schwerin as the heading and lists the matching form “Christian Ludwig, Mecklenburg, Herzog,” with dates 1683–1756. Haskell places the similar commission after the Maximilian passage but does not date it; this card aligns the name and title without adding a biographical claim. The Chinese display name is a project working transliteration.",
        "context_zh": "第10章p.277称其与Rosalba有类似委托并邀请她赴德国；关系候选留待S6。",
        "context_en": "Chapter 10, p. 277, attributes similar commissions and an invitation to Germany to him; the relation candidate remains for S6.",
        "relations": ["st-chp10-p277-christian-louis-rosalba-commissions"],
        "external_note": "Identity comparison only: Deutsche Biographie GND 102111847 gives Christian Ludwig II of Mecklenburg-Schwerin, born 1683 and died 1756, and lists “Christian Ludwig, Mecklenburg, Herzog” as an alternate name. This title/name form matches the index M.csv#145 and Haskell's “Duke Christian Louis of Mecklenburg.” Haskell does not date the commission; no chronology or commission detail is added from the authority record.",
        "s3_note": "Deutsche Biographie GND 102111847 lists “Christian Ludwig, Mecklenburg, Herzog” as an alternate name for Christian Ludwig II of Mecklenburg-Schwerin (1683–1756), matching Haskell's index form and body title. The commission date is unstated, so only the identity/name correspondence is used. No matching person KU exists.",
    },
]

MEMBERS = [
    {
        "candidate": t["candidate"], "initial_group": t["initial_group"], "group": t["group"],
        "ku": t["ku"], "external_source": t["external_source"], "external_id": t["external_id"],
        "external_note": t["external_note"], "s3_note": t["s3_note"],
    }
    for t in TARGETS
]
MEMBERS.append({
    "candidate": "cand-1587",
    "initial_group": "new-person:bavaria-elector-maximilian-of-7d0b923214",
    "group": MAX_GROUP,
    "ku": "units/persons/maximilian-ii-emanuel-of-bavaria",
    "external_source": "Deutsche Biographie",
    "external_id": "11857941X",
    "external_note": TARGETS[2]["external_note"],
    "s3_note": "cand-1587在第10章p.277称Maximilian of Bavaria；Deutsche Biographie GND 11857941X将Maximilian II. Emanuel与Max Emanuel列为同一巴伐利亚选帝侯记录。与cand-1586并入同一new身份组，没有匹配既有person KU。",
})

UNRESOLVED = {
    "candidate": "cand-1525",
    "prior_group": "new-person:mantua-of-73894be007",
    "note": "书后索引M.csv#62及第8章p.216只称‘Marquis of Mantua’，未给个人姓名；旧S3理由误称其为full personal name，现撤回。尚无本批外部记录或书内跨章锚点能把这一头衔唯一对应到具体人物，故由new改为undecided，不登记KU。后续需有据的1656年曼图亚头衔持有人或原始委托记录才能消歧；关系候选st-chp8-p216-magni-working-for-marquis-mantua仍待S6。",
}


def make_card(t):
    sources = []
    for entry, index_name, pages in t["indexes"]:
        sources.append(book_source(
            f"书后索引 {entry}；所列页码{pages}",
            f"索引条目为‘{index_name}’，页码指向{pages}。",
            f"02-sources/03-Index/03-2-Index-CSV/M.csv", entry, [(entry, index_name)],
        ))
    for file, location, summary, quotes in t["chapters"]:
        sources.append(book_source(location, summary, file, "; ".join(span for span, _ in quotes), quotes))
    sources.append(external_source(t["external_citation"], t.get("external_url", t["external_id"]), t["external_location"], t["external_summary"], t["external_quotes"]))
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）", "name_en": t["name_en"], "type": "person",
        "evidence_status": "source_backed", "sources": sources, "created": DATE, "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    rows = "\n".join(f"| {field} | {value} | {ref} |" for field, value, ref in t["name_rows"])
    relation_items = "；".join(f"`{sid}`" for sid in t["relations"])
    external_url = t.get("external_url", t["external_id"])
    body = f"""## 内容

### 描述

**中文：** {t['description_zh']}

**English:** {t['description_en']}

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
{rows}

### 本书相关内容

**中文：** {t['context_zh']} 相关statement：{relation_items}。

**English:** {t['context_en']} Related statements: {relation_items}.

## 关系与证据

### 身份与外部链接

- **{t['external_source']}**: [{t['external_id']}]({external_url}) — 用于身份与名称对应；不单独验证Haskell的关系或委托陈述。

### 关系记录

当前没有登记在 `relations.csv` 中的正式关系。直接S2关系候选 {relation_items} 留待S6审查；本次S4登记不创建正式边。
"""
    return f"---\n{fm}---\n\n{body}"


def insert_accepted(text, card_path):
    lines = text.splitlines()
    entry = f"- {card_path}"
    assert entry not in lines
    units = lines.index("units:")
    claims = next((i for i in range(units + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])), len(lines))
    insert_at = next((i for i in range(units + 1, claims) if lines[i].startswith("- ") and lines[i][2:] > card_path), claims)
    lines.insert(insert_at, entry)
    return "\n".join(lines) + "\n"


def csv_text(fieldnames, rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def base_note_prefix(note):
    match = re.match(r"(.*?); group=[^;]+;", note)
    if match:
        return match.group(1)
    return note


def primary_group_rows(alignments, group):
    return [r for r in alignments if r.get("candidate_id") and not r.get("external_source") and r.get("decision") == "new" and sync.get_group(r.get("resolution_note", "")) == group]


def build_outputs():
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidates_by_id = {r["candidate_id"]: r for r in candidates}
    decisions = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    assert len(decisions) == len(candidates)
    assert UNRESOLVED["candidate"] in decisions and decisions[UNRESOLVED["candidate"]]["decision"] == "new"
    assert sync.get_group(decisions[UNRESOLVED["candidate"]]["resolution_note"]) == UNRESOLVED["prior_group"]
    assert candidates_by_id[UNRESOLVED["candidate"]]["suggested_type"] == "person"
    assert len([r for r in alignments if r.get("candidate_id") == UNRESOLVED["candidate"]]) == 1
    assert len({t["ku"] for t in TARGETS}) == len(TARGETS)
    assert len({t["card"] for t in TARGETS}) == len(TARGETS)
    manifest_ids = {r["ku_id"] for r in manifest}
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    for t in TARGETS:
        assert candidates_by_id[t["candidate"]]["suggested_type"] == "person"
        row = decisions[t["candidate"]]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert sync.get_group(row["resolution_note"]) == t["initial_group"]
        assert t["ku"] not in manifest_ids and not (ROOT / t["card"]).exists()
        assert f"- {t['card']}" not in accepted_text.splitlines()
        assert not any(r.get("candidate_id") == t["candidate"] and r.get("external_source") for r in alignments)
    extra = decisions["cand-1587"]
    assert extra["decision"] == "new" and not extra.get("ku_id")
    assert sync.get_group(extra["resolution_note"]) == "new-person:bavaria-elector-maximilian-of-7d0b923214"
    assert not any(r.get("candidate_id") == "cand-1587" and r.get("external_source") for r in alignments)
    assert len(primary_group_rows(alignments, TARGETS[2]["initial_group"])) == 1
    assert len(primary_group_rows(alignments, "new-person:bavaria-elector-maximilian-of-7d0b923214")) == 1
    assert not any(r.get("ku_id") in {t["ku"] for t in TARGETS} for r in manifest)

    index_text = (ROOT / "02-sources/03-Index/03-2-Index-CSV/M.csv").read_text(encoding="utf-8-sig")
    assert '"Marlborough, Duchess of",,,,278' in index_text
    assert '"Maupertuis, Pierre-Louis",,,,349' in index_text
    assert '"Max Emmanuel, Elector of Bavaria",,,,"193, 278"' in index_text
    assert '"Maximilian, Prince, Elector of Bavaria",,,,277' in index_text
    assert '"Mecklenburg, Christian Louis, Duke of",,,,277' in index_text
    source_checks = {
        "02-sources/02-Markdown/07_CHP-7_sec_iv.md": ["under the new Elector Max Emmanuel"],
        "02-sources/02-Markdown/08_CHP-8_sec_ii.md": ["working for the Marquis of Mantua"],
        "02-sources/02-Markdown/10_CHP-10_intro.md": ["Maximilian of Bavaria", "Duke Christian Louis of", "Elector Max Emmanuel", "the Duchess of Marlborough to Lord Manchester"],
        "02-sources/02-Markdown/14_CHP-14_intro.md": ["met Pierre Crozat, Maupertuis and Voltaire"],
    }
    for file, fragments in source_checks.items():
        content = (ROOT / file).read_text(encoding="utf-8-sig")
        assert all(fragment in content for fragment in fragments), file

    planned_alignments = [dict(r) for r in alignments]
    planned_decisions = {r["candidate_id"]: r for r in planned_alignments if r.get("candidate_id") and not r.get("external_source")}
    unres = next(r for r in planned_alignments if r.get("candidate_id") == UNRESOLVED["candidate"] and not r.get("external_source"))
    unres["decision"] = "undecided"
    unres["ku_id"] = ""
    unres["process_ref"] = PROCESS_REF
    unres["resolution_note"] = base_note_prefix(unres.get("resolution_note", "")) + f"; prior_decision=new; prior_group={UNRESOLVED['prior_group']} (superseded); S3复核（{DATE}）：{UNRESOLVED['note']}"

    external_rows = []
    next_alignment = max(int(r["alignment_id"].split("-")[1]) for r in alignments if re.fullmatch(r"aln-\d+", r["alignment_id"]))
    for member in MEMBERS:
        row = planned_decisions[member["candidate"]]
        prefix = base_note_prefix(row.get("resolution_note", ""))
        prior_groups = (
            ["new-person:bavaria-elector-emmanuel-max-of-185c8d9fb9", "new-person:bavaria-elector-maximilian-of-7d0b923214"]
            if member["candidate"] in {"cand-1586", "cand-1587"}
            else [member["initial_group"]]
        )
        row["resolution_note"] = (
            prefix + "; prior_group=" + "|".join(prior_groups) + f" (superseded); group={member['group']}; "
            + member["s3_note"] + f" S4登记（{DATE}）：映射至{member['ku']}。"
        )
        row["ku_id"] = member["ku"]
        row["process_ref"] = PROCESS_REF
        next_alignment += 1
        ext = {
            "alignment_id": f"aln-{next_alignment}", "candidate_id": member["candidate"], "ku_id": member["ku"],
            "external_source": member["external_source"], "external_id": member["external_id"], "decision": "new",
            "accessed_date": DATE, "process_ref": PROCESS_REF, "legacy_ku_id": "",
            "resolution_note": member["external_note"],
        }
        external_rows.append(ext)
        planned_alignments.append(ext)

    candidates_for_stats = [dict(r) for r in candidates]
    planned_manifest = list(manifest)
    cards = {}
    accepted_new = accepted_text
    for t in TARGETS:
        planned_manifest.append({"ku_id": t["ku"], "type": "person", "canonical_name": t["name_zh"], "name_en": t["name_en"], "source_task": TASK, "card_path": t["card"]})
        accepted_new = insert_accepted(accepted_new, t["card"])
        cards[t["card"]] = make_card(t)
    planned_manifest.sort(key=lambda r: r["ku_id"])

    statements = sync.load_statements()
    member_ids = {m["candidate"] for m in MEMBERS}
    direct = [r for r in statements if any(r.get(field) in {"cand-1525", *member_ids} for field in ("subject_candidate_id", "object_candidate_id"))]
    direct_relation = [r for r in direct if (r.get("qualifiers") or {}).get("relation_candidate") is True]
    expected_relations = {
        "st-chp8-p216-magni-working-for-marquis-mantua", "st-chp10-p278-duchess-wrote-manchester-music-letter",
        "st-chp14-p349-met-maupertuis", "st-chp10-p278-amigoni-max_emmanuel",
        "st-chp10-p277-maximilian-carriera-portrait-commissions", "st-chp10-p277-christian-louis-rosalba-commissions",
    }
    assert {r["statement_id"] for r in direct_relation} == expected_relations, {r["statement_id"] for r in direct_relation}
    assert len(direct) == 6 and len(direct_relation) == 6

    stats = sync.summarize_by_type(candidates_for_stats, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert stats["person"]["registered_groups"] == 599, stats["person"]
    assert stats["person"]["registered_members"] == 692
    assert stats["person"]["pending_groups"] == 463, stats["person"]
    assert stats["person"]["pending_members"] == 464
    assert totals["registered_groups"] == 1008 and totals["registered_members"] == 1186
    assert totals["pending_groups"] == 3762 and totals["pending_members"] == 3776, totals
    assert len(planned_manifest) == len(manifest) + 4

    # Generate the structured name rows and external source registry from the saved-card format.
    with tempfile.TemporaryDirectory(prefix="pnp-s4-m-index-") as temp_dir:
        selected_manifest = []
        for t in TARGETS:
            temp_card = Path(temp_dir) / f"{t['ku'].split('/')[-1]}.md"
            temp_card.write_text(cards[t["card"]], encoding="utf-8")
            selected_manifest.append({"ku_id": t["ku"], "card_path": str(temp_card)})
        additions, source_registry, warnings, cards_with_tables = extract_records(selected_manifest)
    assert cards_with_tables == 4 and not warnings, warnings
    assert len(additions) == sum(len(t["name_rows"]) for t in TARGETS)
    assert all(r["evidence_status"] == "source_backed" and r["source_ids"] for r in additions)
    current_enrichment_text = ENRICHMENT_PATH.read_text(encoding="utf-8-sig")
    existing_enrichment = [json.loads(line) for line in current_enrichment_text.splitlines() if line.strip()]
    assign_ids(additions, ENRICHMENT_PATH)
    ids = {r.get("enrichment_id") for r in existing_enrichment}
    keys = {(r.get("ku_id"), r.get("field"), r.get("value"), r.get("source_id")) for r in existing_enrichment}
    for row in additions:
        assert row["enrichment_id"] not in ids
        key = (row["ku_id"], row["field"], row["value"], row.get("source_id", ""))
        assert key not in keys
        ids.add(row["enrichment_id"])
        keys.add(key)
    planned_enrichment = existing_enrichment + additions

    current_source_rows = sync.read_csv(SOURCES_PATH)[1]
    current_sources_by_id = {r["source_id"]: dict(r) for r in current_source_rows}
    new_sources = sorted(set(source_registry) - set(current_sources_by_id))
    assert len(new_sources) == 4 and all(source_registry[sid]["kind"] == "external" for sid in new_sources)

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    cards_by_ku = {t["ku"]: t for t in TARGETS}
    s4_lines = [
        f"- `{m['candidate']}`（原组`{m['initial_group']}`）→ `{m['group']}` → [{cards_by_ku[m['ku']]['name_zh']}（{cards_by_ku[m['ku']]['name_en']}）](../../../{cards_by_ku[m['ku']]['card']})；{m['s3_note']}"
        for m in MEMBERS
    ]
    s4_lines.insert(2, f"- `cand-1586` 与 `cand-1587` 合并为 `{MAX_GROUP}`，共同映射至一张Maximilian II Emanuel人物卡；Deutsche Biographie GND 11857941X列明Max Emanuel与Maximilian II. Emanuel为同一选帝侯记录。")
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3身份复核与S4人物端点登记：M索引组（{DATE}）\n\n"
        + "\n".join(s4_lines)
        + f"\n- `cand-1525`（原组`{UNRESOLVED['prior_group']}`）由`new`改为`undecided`：{UNRESOLVED['note']}"
        + f"\n\n本批登记4个S3人物组、5条候选映射、4张KU卡及{len(additions)}条source_backed姓名字段；新增5条外部身份对齐行（4个外部记录），并登记{len(new_sources)}个外部来源ID。6条直接S2 relation_candidate（含待证的cand-1525）全部留待S6，未新增formal relation。"
        + f"\n\n登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )
    if not process_text.endswith("\n"):
        process_text += "\n"

    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    alignment_total = len(planned_alignments)
    external_total = sum(bool(r.get("external_source")) for r in planned_alignments)
    result_text, n = re.subn(r"^\| \[全书对齐\].*$", f"| [全书对齐](../tables/alignment.csv) | {sync.fmt(alignment_total)} 条：{sync.fmt(len(candidates))} 条候选决定记录及 {sync.fmt(external_total)} 条外部身份记录；候选决定数见下表 |", result_text, count=1, flags=re.M)
    assert n == 1
    unverified = sum(row.get("evidence_status") == "unverified" for row in existing_enrichment)
    result_text, n = re.subn(r"^\| \[既有字段表\].*$", f"| [既有字段表](../tables/enrichment.jsonl) | {sync.fmt(len(planned_enrichment))}条，其中{sync.fmt(unverified)}条 unverified |", result_text, count=1, flags=re.M)
    assert n == 1
    batch_result = (
        f"### S3复核与S4人物端点：M索引候选组（{DATE}）\n\n"
        + "；\n".join(f"`{m['candidate']}` → `../units/persons/{m['ku'].split('/')[-1]}.md`（`{m['group']}`）" for m in MEMBERS)
        + f"。cand-1586、cand-1587经Deutsche Biographie GND 11857941X合并为一个人物组及一张KU卡。cand-1525由new改为undecided：p.216只有‘Marquis of Mantua’头衔，没有可唯一确认的个人姓名，旧S3 full-name理由撤回。"
        + f"本批6条直接S2 relation_candidate继续待S6；未新增正式关系。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射已登记，{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记；KU={len(planned_manifest)}。"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, batch_result + "\n\n" + marker, 1)

    enrichment_text = "\n".join(json.dumps(row, ensure_ascii=False) for row in planned_enrichment) + "\n"
    alignment_text = csv_text(alignment_fields, planned_alignments)
    manifest_text = csv_text(manifest_fields, planned_manifest)
    # Preserve the existing source registry verbatim and in its established order.
    source_rows = current_source_rows + [source_registry[sid] for sid in new_sources]
    source_text_io = io.StringIO(newline="")
    source_writer = csv.DictWriter(source_text_io, fieldnames=["source_id", "kind", "label", "version", "accessed_date", "citation", "url"], lineterminator="\n")
    source_writer.writeheader()
    source_writer.writerows(source_rows)
    outputs = {
        ALIGNMENT_PATH: alignment_text,
        MANIFEST_PATH: manifest_text,
        ACCEPTED_PATH: accepted_new,
        PROCESS_PATH: process_text,
        RESULT_PATH: result_text,
        ENRICHMENT_PATH: enrichment_text,
        SOURCES_PATH: source_text_io.getvalue(),
        **{ROOT / path: content for path, content in cards.items()},
    }
    return outputs, stats, totals, additions, external_rows, new_sources, direct_relation, planned_manifest


def main():
    parser = argparse.ArgumentParser(description="Review and register the S3/S4 M-index person endpoints.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    outputs, stats, totals, additions, external, new_sources, relations, manifest = build_outputs()
    print(
        f"S3: cand-1525 new->undecided; cand-1586/cand-1587 merged as {MAX_GROUP}; "
        f"S4: groups=4; candidate_mappings=5; cards=4; external_alignment_rows={len(external)}; "
        f"name_rows={len(additions)}; new_external_sources={len(new_sources)}; "
        f"person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; "
        f"person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; "
        f"S4_total={totals['registered_groups']}/{totals['registered_members']} registered, "
        f"{totals['pending_groups']}/{totals['pending_members']} pending; KU={len(manifest)}; "
        f"relation_candidates_pending={len(relations)}; formal_relations_added=0"
    )
    if args.dry_run:
        print("dry-run passed: source/index/context anchors, S3 group coverage, identity mappings, citation registry, and enrichment natural keys; no files changed")
        return
    previous = {path: path.read_bytes() if path.exists() else None for path in outputs}
    try:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            temp = path.with_suffix(path.suffix + ".tmp-s4-m-index")
            temp.write_text(content, encoding="utf-8-sig", newline="\n")
        for path in outputs:
            temp = path.with_suffix(path.suffix + ".tmp-s4-m-index")
            temp.replace(path)
    except Exception:
        for path, original in previous.items():
            if original is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(original)
        raise
    print(f"applied: wrote {len(outputs)} artifacts; enrichment_rows={len(additions)}; new_source_ids={len(new_sources)}")


if __name__ == "__main__":
    main()
