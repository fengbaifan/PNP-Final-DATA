from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."
INDEX_DIR = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV"
ANCHOR = "s4-person-direct-endpoints-canal-carpioni-carracci-catalano-cavagna-cavallino-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BT = chr(96)

TARGETS = [
    {
        "candidate": "cand-0495",
        "group": "new-person:canal-fabio-1d5b97c563",
        "ku": "units/persons/fabio-canal",
        "card": "04-knowledge/units/persons/fabio-canal.md",
        "name_zh": "法比奥·卡纳尔",
        "name_en": "Fabio Canal",
        "name_field": "原文全名",
        "index_entry": "C.csv#19",
        "index_file": "C.csv",
        "index_name": "Canal, Fabio",
        "index_page": "254n",
        "source_fragments": ["Fabio Canal", "Mohnenti"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "source_span": "line 146; print p. 254 n. 2",
                "location": "第9章 p.254 注2；OCR L146",
                "summary": (
                    "Haskell注2转述Molmenti 1909将一幅Grassi壁画归于Fabio Canal，并称其讨论图像内容；注释引文与归属未在本任务中独立查证。"
                ),
                "quote": "- 2 Mohnenti, 1909, pp. 177-88, attributes the fresco to Fabio Canal and unravels the iconography.",
            },
        ],
        "description_zh": (
            "本卡登记Haskell第9章注2点名的Fabio Canal。该注转述Molmenti 1909将一幅Grassi壁画归于Fabio Canal；"
            "这是Haskell对所引文献的报告，原文和归属均未在本任务中独立查证。S3按完整姓名与索引记录建立本书人物组，"
            "没有因姓氏相同而并入既有Canaletto人物卡。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records Fabio Canal named in Chapter 9, note 2. The note reports that Molmenti (1909) attributed a Grassi fresco to Fabio Canal; "
            "the cited publication and attribution were not independently checked in this task. S3 grouped the book's person references under this full name "
            "and index entry; the shared surname did not lead to a merge with the existing Canaletto card. The Chinese name is a working transliteration."
        ),
        "relation_ids": ["st-chp9-p254-note2-molmenti-fabio-canal-attribution"],
        "relation_context_zh": (
            "本项是Haskell注释对Molmenti归属说的转述，非本项目独立确认的作者归属；S2校正OCR“Mohnenti”为Molmenti。保留为S2候选，留待S6。"
        ),
        "relation_context_en": (
            "This is Haskell's report of Molmenti's attribution, not an attribution independently established by this project. S2 corrected OCR “Mohnenti” to "
            "Molmenti from the page image. Preserve it as an S2 candidate for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp9-p254-note2-molmenti-fabio-canal-attribution",
                "cand-8311",
                "cand-0495",
                "molmenti_1909_attributes_grassi_fresco_to_fabio_canal",
                "attributes the fresco to Fabio Canal",
            ),
        ],
    },
    {
        "candidate": "cand-0575",
        "group": "new-person:carpioni-giulio-9a3210b9f2",
        "ku": "units/persons/giulio-carpioni",
        "card": "04-knowledge/units/persons/giulio-carpioni.md",
        "name_zh": "朱利奥·卡尔皮奥尼",
        "name_en": "Giulio Carpioni",
        "name_field": "原文全名",
        "index_entry": "C.csv#99",
        "index_file": "C.csv",
        "index_name": "Carpioni, Giulio",
        "index_page": "393",
        "source_fragments": ["pictures by Giulio", "Carpioni"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md",
                "source_span": "lines 150-151; print p. 393",
                "location": "第19章附录 p.393；OCR L150-151",
                "summary": (
                    "Haskell称1789年匿名拍卖（他将其与John Strange联系）包含若干据称来自Smith收藏的Giulio Carpioni画作；拍卖目录未查，"
                    "来源和单件作品归属不确定。"
                ),
                "quote": "a number of pictures by Giulio Carpioni",
            },
        ],
        "description_zh": (
            "本卡登记Haskell附录中点名的Giulio Carpioni。第393页称，1789年12月10日的匿名拍卖中有若干据称来自Smith收藏的Carpioni画作；"
            "Haskell将该拍卖与John Strange联系。拍卖目录未查，书中也明确说归属不能视为定论。索引以“Carpioni, Giulio”列出该人物。"
            "中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records Giulio Carpioni named in Haskell's appendix. Page 393 says that an anonymous sale on 10 December 1789, which Haskell identifies "
            "with John Strange, included pictures by Carpioni said to have come from Smith's collection. The sale catalogue was not consulted, and Haskell "
            "explicitly cautions that the attributions are not definitive. The index lists “Carpioni, Giulio.” The Chinese name is a working transliteration."
        ),
        "relation_ids": ["st-chp19-p393-1789-carpioni-pictures-attribution"],
        "relation_context_zh": (
            "拍卖记录及作品归属是Haskell转述的未核目录信息；不据此新增正式创作关系，S2候选留待S6。"
        ),
        "relation_context_en": (
            "The sale entry and work attribution are Haskell's report of an unchecked catalogue; no formal creator relation is added, and the S2 candidate remains for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp19-p393-1789-carpioni-pictures-attribution",
                "cand-10825",
                "cand-0575",
                "sale_list_attributed_pictures_to_giulio_carpioni",
                "pictures by Giulio",
            ),
        ],
    },
    {
        "candidate": "cand-0580",
        "group": "new-person:carracci-ludovico-13430870c0",
        "ku": "units/persons/ludovico-carracci",
        "card": "04-knowledge/units/persons/ludovico-carracci.md",
        "name_zh": "卢多维科·卡拉奇",
        "name_en": "Ludovico Carracci",
        "name_field": "原文全名",
        "index_entry": "C.csv#104",
        "index_file": "C.csv",
        "index_name": "Carracci, Ludovico",
        "index_page": "123n, 241, 398",
        "source_fragments": ["Ludovico Carracci", "Lodovico Carracci"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
                "source_span": "line 139; print p. 123 n. 2",
                "location": "第5章 p.123 注2；OCR L139",
                "summary": (
                    "Haskell称Giorgio Nicodemi于1935年发表了Ludovico Carracci写给Carlo的若干书信；该出版物未独立查阅。"
                ),
                "quote": "Some most interesting letters from Ludovico Carracci to Carlo have been published by Giorgio Nicodemi, 1935",
            },
            {
                "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "source_span": "line 28; print p. 398",
                "location": "后记 p.398；OCR L28",
                "summary": (
                    "后记以异拼“Lodovico Carracci”提及Agucchi委托或购得的一幅画；该处为跨章姓名锚点。"
                ),
                "quote": "he had commissioned from Lodovico Carracci",
            },
        ],
        "description_zh": (
            "本卡按跨章身份组登记Ludovico Carracci。第5章注2以“Ludovico Carracci”提及其写给Carlo的书信；后记第398页在谈"
            "Agucchi相关画作时写作“Lodovico Carracci”。本书索引以“Carracci, Ludovico”列出相关页码。两种拼法按S3全名锚点归入同组；"
            "书信出版物未独立查阅。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card registers Ludovico Carracci as a cross-chapter identity group. Chapter 5, note 2, names “Ludovico Carracci” in connection with letters "
            "to Carlo; the postscript on page 398 spells the name “Lodovico Carracci” in its discussion of a picture associated with Agucchi. The index lists "
            "the relevant pages under “Carracci, Ludovico.” S3 grouped the two spellings by the full-name anchor; the cited letter publication was not "
            "independently consulted. The Chinese name is a working transliteration."
        ),
        "relation_ids": ["st-chp5-note-p123-n2-ludovico-letters"],
        "relation_context_zh": (
            "S2候选描述Nicodemi发表书信的书目记录，出版物未独立查阅；后记异拼只作为跨章身份锚点。本批不创建正式关系，候选留待S6。"
        ),
        "relation_context_en": (
            "The S2 candidate records Haskell's bibliographic statement about Nicodemi's publication; that publication was not independently consulted. "
            "The postscript spelling is used only as a cross-chapter identity anchor. No formal relation is added; the candidate remains for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp5-note-p123-n2-ludovico-letters",
                "cand-0580",
                "cand-6095",
                "letters_published_in",
                "letters from Ludovico Carracci to Carlo",
            ),
        ],
    },
    {
        "candidate": "cand-0608",
        "group": "new-person:catalano-francesco-89bacc7e59",
        "ku": "units/persons/francesco-catalano",
        "card": "04-knowledge/units/persons/francesco-catalano.md",
        "name_zh": "弗朗切斯科·卡塔拉诺",
        "name_en": "Francesco Catalano",
        "name_field": "原文全名",
        "index_entry": "C.csv#132",
        "index_file": "C.csv",
        "index_name": "Catalano, Francesco",
        "index_page": "135n",
        "source_fragments": ["Francesco Catalano of Benevento", "accused of stealing two pictures"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/05_CHP-5_sec_iii.md",
                "source_span": "line 136; print p. 135 n. 3",
                "location": "第5章 p.135 注3；OCR L136",
                "summary": (
                    "Haskell转述Bertolotti称Swanevelt曾控告来自Benevento的Francesco Catalano偷窃两幅Van Laer画作；这是指控，不是定罪。"
                ),
                "quote": "reports the case brought by Swanevelt against Francesco Catalano of Benevento whom he accused of stealing two pictures by Van Laer",
            },
        ],
        "description_zh": (
            "本卡登记Haskell第5章注3点名的Francesco Catalano。该注转述Bertolotti记载Swanevelt曾控告来自Benevento的Catalano偷窃两幅"
            "Van Laer画作；原文记录的是诉讼指控，不是已经裁定的盗窃事实。被引材料未在本任务中独立查阅。索引以"
            "“Catalano, Francesco”列出该人物并指向第135页注3。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records Francesco Catalano named in Chapter 5, note 3. The note reports Bertolotti's account of a case brought by Swanevelt against "
            "Catalano of Benevento, who was accused of stealing two Van Laer pictures. The source records an accusation, not an adjudicated finding of theft. "
            "The cited material was not independently consulted in this task. The index lists “Catalano, Francesco” at page 135 note 3. The Chinese name is a "
            "working transliteration."
        ),
        "relation_ids": ["st-chp5-notes-l136-swanevelt-catalano-case"],
        "relation_context_zh": (
            "该S2候选保留Haskell对Bertolotti的转述和“被指控”状态；不把指控写成既定事实，正式关系留待S6。"
        ),
        "relation_context_en": (
            "This S2 candidate preserves Haskell's report of Bertolotti and the status as an accusation; it does not turn the allegation into an established "
            "fact. The formal relation remains for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp5-notes-l136-swanevelt-catalano-case",
                "cand-2535",
                "cand-0608",
                "reported_accusation_of_theft",
                "Francesco Catalano of Benevento",
            ),
        ],
    },
    {
        "candidate": "cand-0611",
        "group": "new-person:cavagna-giampaolo-81fd593733",
        "ku": "units/persons/giampaolo-cavagna",
        "card": "04-knowledge/units/persons/giampaolo-cavagna.md",
        "name_zh": "吉安保罗·卡瓦尼亚",
        "name_en": "Giampaolo Cavagna",
        "name_field": "原文全名",
        "index_entry": "C.csv#135",
        "index_file": "C.csv",
        "index_name": "Cavagna, Giampaolo",
        "index_page": "215",
        "source_fragments": ["Giampaolo", "Cavagna", "completed the decoration of the dome"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "source_span": "lines 14-15; print p. 215",
                "location": "第8章 p.215；OCR L14-15",
                "summary": (
                    "Haskell称Giampaolo Cavagna与两位未具名本地画家完成穹顶天使和先知的壁画装饰；S2将时间按前文限定为1614年。"
                ),
                "quote": "Two years later the Bcrgamasque painter Giampaolo\nCavagna, helped by two other local artists, completed the decoration of the dome with frescoes of angels and prophets.",
            },
        ],
        "description_zh": (
            "本卡登记Haskell第8章点名的Giampaolo Cavagna。第215页称他与两位未具名本地画家完成穹顶天使和先知的壁画装饰；"
            "按前文1612年的时间锚点，S2将完成时间限定为1614年。OCR“Bcrgamasque”已在S2依据纸本校正为“Bergamasque”；"
            "两位协作者仍未具名。索引以“Cavagna, Giampaolo”列出该人物。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records Giampaolo Cavagna named in Chapter 8. Page 215 says that he and two unnamed local artists completed the dome decoration with "
            "angels and prophets; S2 dates the completion to 1614 from the preceding 1612 anchor. S2 corrects OCR “Bcrgamasque” to “Bergamasque” from the "
            "printed page. The two collaborators remain unnamed. The index lists “Cavagna, Giampaolo.” The Chinese name is a working transliteration."
        ),
        "relation_ids": ["st-chp8-p215-cavagna-dome-frescoes-1614"],
        "relation_context_zh": (
            "该候选指Cavagna与两位未具名协作者共同完成的一组穹顶壁画，不推定协作者身份；候选留待S6。"
        ),
        "relation_context_en": (
            "This candidate describes Cavagna completing a dome-fresco group with two unnamed collaborators; their identities are not inferred. The candidate "
            "remains for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp8-p215-cavagna-dome-frescoes-1614",
                "cand-0611",
                "cand-7638",
                "fresco_decoration_completion",
                "Giampaolo",
            ),
        ],
    },
    {
        "candidate": "cand-0613",
        "group": "new-person:bernardo-cavallino-27645d6985",
        "ku": "units/persons/bernardo-cavallino",
        "card": "04-knowledge/units/persons/bernardo-cavallino.md",
        "name_zh": "贝尔纳多·卡瓦利诺",
        "name_en": "Bernardo Cavallino",
        "name_field": "原文全名",
        "index_entry": "C.csv#137",
        "index_file": "C.csv",
        "index_name": "Cavallino, Bernardo",
        "index_page": "208",
        "source_fragments": ["Bernardo CavaUino", "brilliant colouring"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                "source_span": "line 56; print p. 208",
                "location": "第8章 p.208；OCR L56",
                "summary": (
                    "Haskell转述de Dominici称一幅画的绚丽色彩深深影响Bernardo Cavallino；这段引文经Haskell转述，de Dominici原文未独立查阅。"
                ),
                "quote": "profoundly affected Bernardo CavaUino, we learn from de Dominici",
            },
        ],
        "description_zh": (
            "本卡登记Haskell第8章点名的Bernardo Cavallino。该段先谈Rubens的《Herod宴会》，继而转述de Dominici称一幅画的绚丽色彩深深影响"
            "Cavallino；原始de Dominici文本未在本任务中独立查阅。OCR“CavaUino”已由S2按纸本校正为“Cavallino”。索引以"
            "“Cavallino, Bernardo”列出该人物并指向第208页。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records Bernardo Cavallino named in Chapter 8. The passage discusses Rubens's *Feast of Herod* and then reports de Dominici's statement "
            "that a picture's brilliant colouring profoundly affected Cavallino; de Dominici's original text was not independently consulted in this task. "
            "S2 corrects OCR “CavaUino” to “Cavallino” from the printed page. The index lists “Cavallino, Bernardo” at page 208. The Chinese name is a working "
            "transliteration."
        ),
        "relation_ids": ["st-chp8-p208-de-dominici-cavallino-affect"],
        "relation_context_zh": (
            "影响关系来自Haskell对de Dominici的转述，原始文本未查；保留转述与纸本校正限定，正式关系留待S6。"
        ),
        "relation_context_en": (
            "The influence statement is mediated through Haskell's report of de Dominici, whose original text was not consulted. Preserve that qualification "
            "and the print-based name correction; the formal relation remains for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp8-p208-de-dominici-cavallino-affect",
                "cand-0942",
                "cand-0613",
                "de_dominici_reported_rubens_picture_affected_cavallino",
                "profoundly affected Bernardo CavaUino",
            ),
        ],
    },
]


def insert_accepted(lines: list[str], card_path: str) -> list[str]:
    units_idx = lines.index("units:")
    claims_idx = next(
        (i for i in range(units_idx + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])),
        len(lines),
    )
    entry = f"- {card_path}"
    assert entry not in lines
    insert_at = next(
        (i for i in range(units_idx + 1, claims_idx) if lines[i].startswith("- ") and lines[i][2:] > card_path),
        claims_idx,
    )
    lines.insert(insert_at, entry)
    return lines


def read_index_rows(file_name: str) -> list[dict[str, str]]:
    raw = (INDEX_DIR / file_name).read_bytes()
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        content = raw.decode("cp1252")
    return list(csv.DictReader(io.StringIO(content)))


def make_card(t: dict) -> str:
    sources = [
        {
            "citation": INDEX_CITATION,
            "location": f"全书索引 {t['index_entry']}；所列页码{t['index_page']}",
            "sentence_summary": f"索引主项为“{t['index_name']}”，页码指向{t['index_page']}。",
            "original_quotes": [{"source_span": t["index_entry"], "text": t["index_name"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/03-Index/03-2-Index-CSV/{t['index_file']}",
                "source_span": t["index_entry"],
            },
        },
    ]
    for source in t["book_sources"]:
        sources.append(
            {
                "citation": BOOK,
                "location": source["location"],
                "sentence_summary": source["summary"],
                "original_quotes": [{"source_span": source["source_span"], "text": source["quote"]}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": source["source_file"],
                    "source_span": source["source_span"],
                },
            }
        )
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）",
        "name_en": t["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    links = [
        f"[{source['location']}](../../../{source['source_file']})"
        for source in t["book_sources"]
    ]
    links.append(
        f"[索引 {t['index_entry']}](../../../02-sources/03-Index/03-2-Index-CSV/{t['index_file']})"
    )
    evidence_links = " ".join(links)
    relation_list = ", ".join(f"{BT}{sid}{BT}" for sid in t["relation_ids"])
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {t['description_zh']} {evidence_links}

**English:** {t['description_en']} {evidence_links}

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| {t['name_field']} | {t['index_name']} | S1（索引 {t['index_entry']}） |

### 本书相关内容

**中文：** {t['relation_context_zh']} {evidence_links}

**English:** {t['relation_context_en']} {evidence_links}

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

当前没有登记在 relations.csv 中的正式关系。直接S2候选 {relation_list} 留待S6审查；本次S4登记不裁决或创建正式关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register six source-backed new person groups in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
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

    for t in TARGETS:
        cid = t["candidate"]
        c = candidate_by_id[cid]
        a = alignment_by_id[cid]
        assert c.get("suggested_type") == "person"
        assert a.get("decision") == "new" and not a.get("ku_id")
        assert sync.get_group(a.get("resolution_note", "")) == t["group"]
        assert c.get("index_entry_id") == t["index_entry"]
        assert c.get("canonical_name") == t["index_name"]
        group_members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == t["group"]
        ]
        assert group_members == [cid], (t["group"], group_members)
        index_row_number = int(t["index_entry"].split("#")[1])
        index_row = read_index_rows(t["index_file"])[index_row_number]
        assert index_row.get("Main Entry") == t["index_name"]
        assert index_row.get("Page Numbers", "") == t["index_page"]
        combined_source_text = "\n".join(
            (ROOT / source_file).read_text(encoding="utf-8-sig")
            for source_file in {s["source_file"] for s in t["book_sources"]}
        )
        assert all(fragment in combined_source_text for fragment in t["source_fragments"]), cid
        normalized_source = re.sub(r"\s+", " ", combined_source_text)
        for source in t["book_sources"]:
            assert re.sub(r"\s+", " ", source["quote"]) in normalized_source, (
                cid, source["source_span"], source["quote"]
            )
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
            assert quote_fragment in statement.get("original_quote", ""), (
                sid, quote_fragment, statement.get("original_quote", "")
            )
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
        a["resolution_note"] += (
            f" S4登记（{DATE}）：{t['group']} 映射至 {t['ku']}；书内索引与正文共同支持source-local人物登记，"
            "原文限定与待证事项保留，直接关系候选仍待S6。"
        )
        planned_manifest.append(
            {
                "ku_id": t["ku"],
                "type": "person",
                "canonical_name": t["name_zh"],
                "name_en": t["name_en"],
                "source_task": TASK,
                "card_path": t["card"],
            }
        )
    planned_manifest.sort(key=lambda row: row["ku_id"])

    planned_accepted = accepted_lines
    for t in TARGETS:
        planned_accepted = insert_accepted(planned_accepted, t["card"])
    assert len(accepted_paths) + len(TARGETS) == len(
        {line[2:] for line in planned_accepted if line.startswith("- 04-knowledge/units/")}
    )

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] == 763 and totals["registered_members"] == 934
    assert totals["pending_groups"] == 4013 and totals["pending_members"] == 4027
    assert stats["person"]["registered_groups"] == 357
    assert stats["person"]["registered_members"] == 443
    assert stats["person"]["pending_groups"] == 711
    assert stats["person"]["pending_members"] == 712
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    cards = {t["card"]: make_card(t) for t in TARGETS}
    for card in cards.values():
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert match and isinstance(yaml.safe_load(match.group(1)), dict)

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    group_lines = []
    for t in TARGETS:
        statements_text = ", ".join(f"{BT}{sid}{BT}" for sid in t["relation_ids"])
        group_lines.append(
            f"- {BT}{t['candidate']}{BT}（{BT}{t['group']}{BT}）→ "
            f"[{t['name_zh']}（{t['name_en']}）](../../../{t['card']})；"
            f"S2直接关系候选 {statements_text} 留待S6；{t['relation_context_zh']}"
        )
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物：六组直接关系端点身份组登记（{DATE}）\n\n"
        + "\n".join(group_lines)
        + "\n\n本批登记6个单候选S3 new人物组，每组映射至一张KU；姓名、来源锚点与候选关系均逐项对应。"
        "Fabio Canal与Canaletto因完整姓名不同而分卡，不据共有姓氏合并；Carracci的Ludovico/Lodovico异拼按S3全名组保留；"
        "Carpioni拍卖归属、Catalano盗窃指控、Cavagna未具名协作者及Cavallino转引来源的限定均保留。"
        "本批没有添加外部身份事实或formal relations。\n\n"
        f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        f"{sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text, n = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>",
        result_text,
        count=1,
    )
    assert n == 1
    result_text += (
        f"\n\n### S4 人物身份组登记：六个直接关系端点（{DATE}）\n\n"
        + "；".join(
            f"{BT}{t['candidate']}{BT} → {BT}../units/persons/{t['ku'].split('/')[-1]}.md{BT}"
            for t in TARGETS
        )
        + "。六组均为S3单候选new组；姓名字段和书内依据可追溯。有关归属、指控、日期、拼写及引文限制见对应卡片。"
        "S2关系候选留待S6，本批不创建formal relations。"
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
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
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
