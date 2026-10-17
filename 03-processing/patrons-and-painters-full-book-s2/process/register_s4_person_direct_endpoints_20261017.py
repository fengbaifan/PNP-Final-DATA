from __future__ import annotations

import argparse
import re
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
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

PEOPLE = [
    {
        "candidate": "cand-0530",
        "group": "new-person:angelo-canini-giovanni-adbabef3e8",
        "ku_id": "units/persons/giovanni-angelo-canini",
        "card_rel": "04-knowledge/units/persons/giovanni-angelo-canini.md",
        "canonical_name": "乔瓦尼·安杰洛·卡尼尼",
        "name_en": "Giovanni Angelo Canini",
        "index_id": "C.csv#54",
        "index_name": "Canini, Giovanni Angelo",
        "index_pages": "154, 161, 187n, 197n",
        "index_file": "02-sources/03-Index/03-1-Index-MD/C.md",
        "index_quote": "| Canini, Giovanni Angelo |  |  |  | 154, 161, 187n, 197n |",
        "relations": {
            "st-chp6-p154-canini-and-gaulli-palace-works",
            "st-chp6-p161-canini-faithful-pupil-of-domenichino",
            "st-chp6-p161-canini-protege-of-bellori",
            "st-chp6-p161-christina-patronizes-canini-with-bellori-guidance",
            "st-chp7-p197-n2-killigrew-portrait",
        },
        "mentions": 3,
        "sources": [
            {
                "location": "第6章；印刷页154；OCR L97",
                "summary": "Haskell 称 Giovanni Angelo Canini 曾随 Cardinal Flavio Chigi 到 Paris 绘写其感兴趣的场景；原文说的是绘写目的，不证明完成了哪些图稿。",
                "quotes": [("line 97", "there were other ceilings by Giovanni Angelo Canini whom the Cardinal had taken with him to draw scenes of interest on his humiliating visit to Paris;")],
                "file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
                "span": "line 97; print p. 154",
            },
            {
                "location": "第6章；印刷页161；OCR L53",
                "summary": "Haskell 以 Gianangelo Canini 指称 Domenichino 的学生及 Bellori 的 protégé；同一段记 Bellori 鼓励 Christina 赞助他。",
                "quotes": [("line 53", "When she let herself be guided by Bellori, the results were different, for he encouraged her to patronise one of Domenichino’s most faithful pupils and a protege of his own, Gianangelo Canini.")],
                "file": "02-sources/02-Markdown/06_CHP-6_sec_iv.md",
                "span": "line 53; print p. 161",
            },
            {
                "location": "第7章；印刷页197；注2；OCR L109",
                "summary": "Haskell 注2将 Thomas Killigrew 肖像归为 Canini 作于1651年；注中所引 Vertue 尚未独立核读。",
                "quotes": [("line 109", "2 Killigrew by Canini in 1651—Vertue, I, p. 114; James Altham as a hermit by Salvator Rosa in 1665 (Bankes Collection)—Italian Art and Britain, p. 20; Sir Thomas Baines by Carlo Dolci between 1665 and 1670 (Fitzwilliam Museum, Cambridge)—ibid., p. 19.")],
                "file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "span": "line 109; print p. 197; footnote 2",
            },
        ],
        "description_zh": (
            "第6章 p.154 以 Giovanni Angelo Canini 称其随 Cardinal Flavio Chigi 到 Paris 绘写场景；"
            "第6章 p.161 使用 Gianangelo Canini，并将其置于 Domenichino 学生、Bellori protégé 的语境。"
            "索引 C.csv#54 将其定位至 p.154、161、187n、197n；第7章 p.197 注2把 Thomas Killigrew 肖像归给 Canini 并记为1651年，"
            "但所引 Vertue 未独立核读。此卡只登记书内全名及同一索引组中的姓名形式，不把待审关系候选转为正式关系。"
        ),
        "description_en": (
            "Chapter 6, p.154, names Giovanni Angelo Canini as accompanying Cardinal Flavio Chigi to Paris to draw scenes; "
            "p.161 uses Gianangelo Canini in the context of a pupil of Domenichino and a protégé of Bellori. "
            "Index entry C.csv#54 locates the person at pp.154, 161, 187n and 197n. Chapter 7, p.197, note 2 attributes "
            "Thomas Killigrew’s portrait to Canini and dates it to 1651, but the cited Vertue has not been independently consulted. "
            "This card records the name and index-grouped forms in the book; it does not turn pending relation candidates into formal relations."
        ),
        "name_note_zh": "书内全名为 Giovanni Angelo Canini；第6章 p.161 写作 Gianangelo Canini。中文名为工作音译。",
        "name_note_en": "The book gives Giovanni Angelo Canini and uses the spelling Gianangelo Canini on p.161. The Chinese display name is a working transliteration.",
        "boundary_zh": "本卡对应 C.csv#54 的索引人物组。Giovanni Angelo 与 Gianangelo 依据该索引组及正文语境归于同一书内人物；本轮未查阅外部身份记录。p.197 注2的肖像归属仍是 Haskell 引述的脚注主张。",
        "boundary_en": "This card represents the person grouped under index entry C.csv#54. Giovanni Angelo and Gianangelo are treated as forms for the same book-local person based on the index grouping and narrative context; no external identity authority was consulted. The portrait attribution in p.197 note 2 remains Haskell’s footnote claim.",
        "chapter_links": [
            ("第6章 p.154", "02-sources/02-Markdown/06_CHP-6_sec_i.md", "（L97）"),
            ("第6章 p.161", "02-sources/02-Markdown/06_CHP-6_sec_iv.md", "（L53）"),
            ("第7章 p.197", "02-sources/02-Markdown/07_CHP-7_sec_iv.md", "（L109）"),
        ],
    },
    {
        "candidate": "cand-0465",
        "group": "new-person:buckingham-john-of-sheffield-7b3adca9be",
        "ku_id": "units/persons/john-sheffield-duke-of-buckingham",
        "card_rel": "04-knowledge/units/persons/john-sheffield-duke-of-buckingham.md",
        "canonical_name": "约翰·谢菲尔德",
        "name_en": "John Sheffield",
        "index_id": "B.csv#313",
        "index_name": "Buckingham, John Sheffield, Duke of",
        "index_pages": "280, 281",
        "index_file": "02-sources/03-Index/03-1-Index-MD/B.md",
        "index_quote": "| Buckingham, John Sheffield, Duke of |  |  |  | 280, 281 |",
        "relations": {
            "st-chp10-p280-bellucci-patron-sheffield-also-employed-ricci",
            "st-chp10-p280-sheffield-description-open",
            "st-chp10-p280-sheffield-supported-jamesii",
            "st-chp10-p280-sheffield-third-wife-jamesii-daughter",
            "st-chp10-p280-sheffield-title-house-politics",
            "st-chp10-p281-sheffield-ceiling-description",
            "st-chp10-p281-sheffield-favourite-anne",
        },
        "mentions": 14,
        "sources": [
            {
                "location": "第10章；印刷页280；OCR L61",
                "summary": "Haskell 以 John Sheffield 全名和 Buckingham 公爵身份标识人物，并称他1703年起任公爵；正文同时提到其雇用 Ricci 及宅邸营建。",
                "quotes": [("line 61", "Indeed, one of his first patrons was a man who had already given employment to Sebastiano Ricci. John Sheffield, Duke of Buckingham since 1703, in which year he had begun to have built his great London house, stood politically rather outside the circles which have so far been considered.")],
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "span": "line 61; print p. 280",
            },
            {
                "location": "第10章；印刷页281；OCR L126",
                "summary": "Haskell 记 Sheffield 在 Queen Anne 去世后退出政坛，并称其当时67岁；按原书叙述记录。",
                "quotes": [("line 126", "when she died he retired from politics. He was by then aged 67 and despite his political affiliations had acquired a great and influential position in society.")],
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "span": "line 126; print p. 281",
            },
        ],
        "description_zh": (
            "第10章以 John Sheffield 全名称其为 Buckingham 公爵，并将其任爵起点记为1703年；同段说他是 Bellucci 的早期赞助人之一，"
            "且此前已雇用 Sebastiano Ricci。第281页记 Haskell 所述其在女王去世后退出政坛、当时67岁。"
            "本卡以书内全名和头衔为身份依据，不将未具名的第三任妻子另行识别，也不把候选关系登记为正式边。"
        ),
        "description_en": (
            "Chapter 10 names John Sheffield as Duke of Buckingham and dates his dukedom from 1703; the same passage says he was "
            "one of Bellucci’s early patrons and had previously employed Sebastiano Ricci. Page 281 records Haskell’s account that "
            "he retired from politics after the queen’s death, aged 67. This card identifies him by the name and title given in the book; "
            "it does not identify the unnamed third wife or convert candidate relations into formal edges."
        ),
        "name_note_zh": "书内全名为 John Sheffield；索引采用 Buckingham, John Sheffield, Duke of 形式。中文名为工作音译。",
        "name_note_en": "The book gives the personal name John Sheffield; the index files him as Buckingham, John Sheffield, Duke of. The Chinese display name is a working transliteration.",
        "boundary_zh": "本卡只指第10章 pp.280–281 所述 John Sheffield。头衔和人物身份依 Haskell 本书记录；本轮未补外部生平或未具名妻子的身份。",
        "boundary_en": "This card refers only to the John Sheffield discussed in Chapter 10, pp.280–281. The title and identity follow Haskell’s account; no external biography or identity for the unnamed wife is added.",
        "chapter_links": [
            ("第10章 p.280", "02-sources/02-Markdown/10_CHP-10_intro.md", "（L61）"),
            ("第10章 p.281", "02-sources/02-Markdown/10_CHP-10_intro.md", "（L126）"),
        ],
    },
    {
        "candidate": "cand-2420",
        "group": "new-person:giacomo-mgr-serra-5c15ad9cae",
        "ku_id": "units/persons/giacomo-serra",
        "card_rel": "04-knowledge/units/persons/giacomo-serra.md",
        "canonical_name": "贾科莫·塞拉",
        "name_en": "Giacomo Serra",
        "index_id": "S.csv#108",
        "index_name": "Serra, Mgr Giacomo",
        "index_pages": "70, 71",
        "index_file": "02-sources/03-Index/03-1-Index-MD/S.md",
        "index_quote": "| Serra, Mgr Giacomo |  |  |  | 70, 71 |",
        "relations": {
            "st-chp3-secii-l144-179-serra-threat-reluctant-agreement",
            "st-chp3-secii-l54-60-conditional-300-scudi-offer",
            "st-chp3-secii-l54-60-serra-anxious-to-promote-rubens",
            "st-chp3-secii-l54-60-serra-approached-oratorians-in-crisis",
            "st-chp3-secii-p70-note3-serra-guercino-patronage",
        },
        "mentions": 8,
        "sources": [
            {
                "location": "第3章；印刷页70；OCR L59–60",
                "summary": "Haskell 以 Monsignor Giacomo Serra 全名介绍这位教士，并叙述他希望促成 Rubens 承接奥拉托利会祭坛画。",
                "quotes": [("lines 59–60", "they were approached by a highly influential cleric, Monsignor Giacomo Serra. He was interested in an artist whom he was particularly anxious to promote, a young Flemish painter Peter Paul Rubens.")],
                "file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "span": "lines 59–60; print p. 70",
            },
            {
                "location": "第3章；印刷页71；OCR L159",
                "summary": "Haskell 记 Serra 表示若神父们不接受条件，他会把钱转给别处；奥拉托利会勉强接受。",
                "quotes": [("line 159", "if they did not accept his terms he would give away his money elsewhere, and so, rather reluctantly, they agreed.")],
                "file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "span": "line 159; print p. 71",
            },
            {
                "location": "第3章；印刷页70；注3；OCR L158",
                "summary": "Haskell 注3称 Serra 也是年轻 Guercino 的赞助人，并引用 Mahon；所引研究本轮未独立核读。",
                "quotes": [("line 158", "3 Serra was also a patron of the young Guercino—see Mahon, 1947, pp. 67-71.")],
                "file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "span": "line 158; print p. 70; footnote 3",
            },
        ],
        "description_zh": (
            "第3章 p.70 以 Monsignor Giacomo Serra 全名介绍人物，并称他积极推动年轻画家 Peter Paul Rubens 获得奥拉托利会祭坛画委托，"
            "愿意承担300 scudi。第71页记其以撤回资助相劝，神父们随后勉强接受条件。第70页注3另称 Serra 是年轻 Guercino 的赞助人，"
            "但 Haskell 引用的 Mahon 尚未独立核读。本卡只据书内姓名与语境登记此人物，不补外部生平。"
        ),
        "description_en": (
            "Chapter 3, p.70, names Monsignor Giacomo Serra and says he sought to secure the Oratorians’ altarpiece commission for "
            "the young Peter Paul Rubens, offering 300 scudi. Page 71 recounts his threat to redirect the money and the fathers’ reluctant "
            "acceptance. Note 3 on p.70 also calls Serra a patron of the young Guercino, citing Mahon, which has not been independently consulted. "
            "This card registers the person from the name and context in the book and adds no external biography."
        ),
        "name_note_zh": "书内称谓为 Monsignor Giacomo Serra，索引形式为 Serra, Mgr Giacomo。中文名为工作音译。",
        "name_note_en": "The book calls him Monsignor Giacomo Serra; the index uses Serra, Mgr Giacomo. The Chinese display name is a working transliteration.",
        "boundary_zh": "本卡只指第3章 pp.70–71 中的 Monsignor Giacomo Serra。Monsignor 保留为书内称谓，不据此补充任职、具体教区或外部身份。脚注所引 Mahon 未独立查阅。",
        "boundary_en": "This card refers only to Monsignor Giacomo Serra in Chapter 3, pp.70–71. Monsignor is retained as the book’s form of address; no office, diocese, or external identity is inferred. Mahon, cited in the footnote, has not been independently consulted.",
        "chapter_links": [
            ("第3章 p.70", "02-sources/02-Markdown/03_CHP-3_sec_ii.md", "（L59–60、L158）"),
            ("第3章 p.71", "02-sources/02-Markdown/03_CHP-3_sec_ii.md", "（L159）"),
        ],
    },
]


def make_card(person: dict) -> str:
    source_rows = []
    for item in person["sources"]:
        source_rows.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [
                {"source_span": span, "text": quote}
                for span, quote in item["quotes"]
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["file"],
                "source_span": item["span"],
            },
        })
    source_rows.append({
        "citation": BOOK_CITATION,
        "location": f"书后索引；{person['index_id']}；印刷页{person['index_pages']}",
        "sentence_summary": f"书后索引以 {person['index_name']} 形式列出人物及本条页码定位。",
        "original_quotes": [
            {"source_span": f"index entry {person['index_id']}", "text": person["index_quote"]}
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": person["index_file"],
            "source_span": f"index entry {person['index_id']}",
        },
    })
    frontmatter = {
        "title": f"{person['canonical_name']}（{person['name_en']}）",
        "name_en": person["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    links = "; ".join(
        f"[{label}](../../../{path}){span}"
        for label, path, span in person["chapter_links"]
    )
    relation_ids = ", ".join(sorted(person["relations"]))
    body = f"""## 内容

### 描述

**中文：** {person['description_zh']} [来源定位：{links}；[书后索引](../../../{person['index_file']})（{person['index_id']}）]

**English:** {person['description_en']} [Sources: {links}; [Index](../../../{person['index_file']}) ({person['index_id']})]

### 名称

{person['name_note_zh']}

{person['name_note_en']}

### 身份边界

{person['boundary_zh']}

{person['boundary_en']}

## 关系与证据

本轮只登记人物身份；以下 {len(person['relations'])} 条直接 S2 `relation_candidate` 保留待 S6，未新增正式关系：{relation_ids}。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register direct person relation endpoints in S4 by S3 identity group.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    _, mentions = sync.read_csv(TABLES / "mentions.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_alignments = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    statements = sync.load_statements()
    manifest_names = {
        (row.get("name_en") or "").casefold()
        for row in manifest if row.get("type") == "person"
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    seen_candidate_ids = set()
    for person in PEOPLE:
        cid = person["candidate"]
        candidate = candidate_by_id[cid]
        alignment = candidate_alignments[cid]
        assert candidate["index_entry_id"] == person["index_id"]
        assert candidate["canonical_name"] == person["index_name"]
        assert candidate["index_page_range"] == person["index_pages"]
        assert candidate["suggested_type"] == "person"
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == person["group"]
        group_rows = [
            row for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == person["group"]
        ]
        assert [row["candidate_id"] for row in group_rows] == [cid]
        assert person["name_en"].casefold() not in manifest_names
        assert not (ROOT / person["card_rel"]).exists()
        assert person["card_rel"] not in accepted
        assert cid not in seen_candidate_ids
        seen_candidate_ids.add(cid)
        source_text = "\n".join(
            (ROOT / item["file"]).read_text(encoding="utf-8-sig")
            for item in person["sources"]
        )
        for _, path, _ in person["chapter_links"]:
            assert (ROOT / path).exists(), path
        index = (ROOT / person["index_file"]).read_text(encoding="utf-8-sig")
        assert person["index_quote"] in index
        assert len([m for m in mentions if m.get("candidate_id") == cid]) == person["mentions"]
        direct_relation_ids = {
            row["statement_id"] for row in statements
            if (row.get("subject_candidate_id") == cid or row.get("object_candidate_id") == cid)
            and (row.get("qualifiers") or {}).get("relation_candidate") is True
        }
        assert direct_relation_ids == person["relations"], (cid, direct_relation_ids)
        assert source_text.strip()

    planned_alignment = [dict(row) for row in alignments]
    for person in PEOPLE:
        row = next(r for r in planned_alignment if r.get("candidate_id") == person["candidate"])
        row["ku_id"] = person["ku_id"]
        row["resolution_note"] += f" S4 registration: mapped {person['group']} to {person['ku_id']}."
    planned_manifest = list(manifest)
    for person in PEOPLE:
        planned_manifest.append({
            "ku_id": person["ku_id"],
            "type": "person",
            "canonical_name": person["canonical_name"],
            "name_en": person["name_en"],
            "source_task": TASK,
            "card_path": person["card_rel"],
        })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text, n = re.subn(
        r"^\| \[既有字段表\]\(\.\./tables/enrichment\.jsonl\) \|.*$",
        "| [既有字段表](../tables/enrichment.jsonl) | 10,509条，其中1,611条 unverified |",
        result_text, count=1, flags=re.M,
    )
    assert n == 1
    audit_line = (
        "2026-10-17 strict-stage 表审计通过：`errors=[]`、`s2_missing=[]`。审计警告中的4,549条待登记 "
        "`decision=new` alignment 行，含4,534条候选决定映射（4,464组）和15条外部身份记录。另有两条既有字段来源引用未能从对应卡片source列表解析 "
        "（`enr-06678`、`enr-06937`）；相关字段仍保留原状态。审计还提示S2迁移的语义质量仍须按关联过程记录检查；结构一致性不代表独立语义验收，也不产生准确率、召回率或语义处理吞吐指标。"
    )
    result_text, n = re.subn(
        r"^\d{4}-\d{2}-\d{2} strict-stage 表审计通过：.*$",
        audit_line, result_text, count=1, flags=re.M,
    )
    assert n == 1
    result_lines = []
    for person in PEOPLE:
        result_lines.append(
            f"\n\n### S4 person：{person['name_en']} 直接关系端点身份组（2026-10-17）\n\n"
            f"`{person['candidate']}`（{person['index_id']}）按 S3 组 `{person['group']}` 登记至"
            f"[{person['canonical_name']}人物卡](../units/persons/{Path(person['card_rel']).stem}.md)。"
            f"索引页码 {person['index_pages']} 与书内全名／变体相互定位；本卡仅记录 Haskell 可支持的身份与叙述，"
            "脚注所引研究未独立核读，身份不扩展至未具名对象或外部传记。"
            f"{len(person['relations'])}条直接关系候选保留待 S6，不新增正式关系。"
            f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
            f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
        )
    result_text += "".join(result_lines)

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += "\n\n### S4 person 批次：直接关系端点（2026-10-17）\n\n"
    for person in PEOPLE:
        process_text += (
            f"#### {person['name_en']}（{person['canonical_name']}）\n\n"
            f"候选 `{person['candidate']}`（{person['index_id']}；索引定位 {person['index_pages']}）保持 S3 `new` 组 "
            f"`{person['group']}`，单候选映射至[人物卡](../../../{person['card_rel']})；同组只登记一个 KU。"
            f"书内主要证据与身份边界：{person['description_zh']} "
            f"{len(person['relations'])}条直接 relation_candidate 原样保留待 S6：{', '.join(sorted(person['relations']))}。"
            "不将候选关系写入 relations.csv；未新增 enrichment 字段事实或 sources.csv 登记。\n\n"
        )
    process_text += (
        "本批没有外部身份记录；所引 Haskell 脚注中的 Pascoli、Vertue、Mahon 等材料未独立核读。"
        "Canini 的 Giovanni Angelo / Gianangelo 拼写按同一索引主项及正文语境登记；未按姓氏合并其他人。"
        "Sheffield 的未具名第三任妻子不另造人物；Serra 的 Monsignor 保留为原书称谓，不外推职务或教区。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    accepted_lines = accepted.splitlines()
    for person in sorted(PEOPLE, key=lambda x: x["card_rel"]):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > person["card_rel"]),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {person['card_rel']}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print("S4 direct-person batch dry-run passed")
        for person in PEOPLE:
            print(f"{person['candidate']} -> {person['ku_id']}; group={person['group']}; relations={len(person['relations'])}")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    for person in PEOPLE:
        (ROOT / person["card_rel"]).write_text(make_card(person), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups={len(PEOPLE)}; registered={sync.fmt(totals['registered_groups'])}/"
        f"{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/"
        f"{sync.fmt(totals['pending_members'])}; manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
