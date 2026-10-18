from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_person_relation_endpoints_allegrini_bouchardon_20261018 as person_sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
DATE = "2026-10-18"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ANCHOR = "s4-schmidt-schonborn-person-endpoints-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def book_source(source_file: str, location: str, span: str, quote: str, summary: str) -> dict:
    return {
        "citation": BOOK,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": source_file,
            "source_span": span,
        },
    }


def index_source(t: dict) -> dict:
    return {
        "citation": "Francis Haskell, *Patrons and Painters*, index, S.csv.",
        "location": f"书后索引，{t['index_entry']}；指向印刷页{t['index_page']}",
        "sentence_summary": f"索引以“{t['index_name']}”为主条并指向印刷页{t['index_page']}。",
        "original_quotes": [{"source_span": t["index_entry"], "text": t["index_name"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": "02-sources/03-Index/03-2-Index-CSV/S.csv",
            "source_span": t["index_entry"],
        },
    }


TARGETS = [
    {
        "candidate": "cand-2396",
        "group": "new-person:friedrich-georg-schmidt-91439cc794",
        "ku": "units/persons/georg-friedrich-schmidt",
        "card": "04-knowledge/units/persons/georg-friedrich-schmidt.md",
        "name_zh": "格奥尔格·弗里德里希·施密特",
        "name_en": "Georg Friedrich Schmidt",
        "index_entry": "S.csv#84",
        "index_name": "Schmidt, Georg Friedrich",
        "index_page": "409",
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "book_sources": [
            book_source(
                "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "第20章后记，印刷页409，行195–197",
                "lines 195–197; print p. 409",
                "The late Dr Maria Santifaller published a series of articles bearing on Algarotti.\n"
                "She showed that the vast majority of portraits of him—of which she illustrated some hitherto not known—were derived from the classicising print made in Berlin by\n"
                "Georg Friedrich Schmidt in 1752, a year after the same artist had etched for Algarotti the rather epicene features of a singer called Felice Salimbeni;6",
                "Haskell称Maria Santifaller指出，Algarotti的大多数肖像源自Georg Friedrich Schmidt于1752年在柏林制作的古典化版画；同段称Schmidt此前为Algarotti蚀刻过歌手Felice Salimbeni的肖像。",
            )
        ],
        "name_rows": [
            ("索引姓名", "Schmidt, Georg Friedrich", "S1，S.csv#84"),
            ("正文姓名", "Georg Friedrich Schmidt", "S2，第20章后记，p.409，L197"),
        ],
        "relation_ids": [
            "st-chp20-p409-santifaller-algarotti-portraits-schmidt-print",
            "st-chp20-p409-schmidt-salimbeni-etching",
        ],
        "description_zh": (
            "本卡登记书后索引作“Schmidt, Georg Friedrich”、第20章后记具名的Georg Friedrich Schmidt。"
            "Haskell转述Maria Santifaller的研究，称Algarotti的大多数肖像源自Schmidt于1752年在柏林制作的版画；"
            "同段称Schmidt此前为Algarotti蚀刻过歌手Felice Salimbeni的肖像。此处仅记录书内识别与归因，不独立核验相关版画或研究结论。"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Georg Friedrich Schmidt, indexed as “Schmidt, Georg Friedrich” and named in Chapter 20's postscript. "
            "Haskell reports Maria Santifaller's finding that most portraits of Algarotti derived from a print Schmidt made in Berlin in 1752; "
            "the same passage says Schmidt had etched a portrait of the singer Felice Salimbeni for Algarotti. "
            "This records the book's identification and attribution without independently verifying the print or the reported scholarship. "
            "The Chinese display name is a working transliteration."
        ),
        "context_zh": (
            "两条涉及Schmidt的S2关系候选分别涉及Algarotti肖像与1752年版画、以及为Felice Salimbeni制作的蚀刻像；"
            "保留原书归因并待S6逐条裁决。"
        ),
        "context_en": (
            "The two S2 relation candidates involving Schmidt concern the 1752 print used for portraits of Algarotti and the etching of Felice Salimbeni. "
            "Both remain source-attributed candidates for separate S6 decisions."
        ),
    },
    {
        "candidate": "cand-2397",
        "group": "new-person:friedrich-karl-schonborn-ec83d66570",
        "ku": "units/persons/friedrich-karl-schonborn",
        "card": "04-knowledge/units/persons/friedrich-karl-schonborn.md",
        "name_zh": "弗里德里希·卡尔·申伯恩",
        "name_en": "Friedrich Karl Schönborn",
        "index_entry": "S.csv#85",
        "index_name": "Schönborn, Friedrich Karl",
        "index_page": "293n, 296",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "book_sources": [
            book_source(
                "02-sources/02-Markdown/10_CHP-10_intro.md",
                "第10章，印刷页296，行320",
                "line 320; print p. 296",
                "after the death of Frederick Karl in 1746 and a short interval under his successor it was taken over by Karl Philip von Greiffenklau.",
                "Haskell称Würzburg主教职位在Frederick Karl于1746年去世及一段短暂继任期后转归Karl Philip von Greiffenklau。",
            ),
            book_source(
                "02-sources/02-Markdown/10_CHP-10_intro.md",
                "第10章脚注4，印刷页293，行560",
                "line 560; print p. 293 n. 4",
                "A letter from Johann Philip Franz to Friedrich Karl Schönborn dated 12 July 1723 to introduce Pellegrini speaks of his success in London, Paris and Diisseldorf—Von Freeden, 1955, p. 848.",
                "Haskell脚注据Von Freeden称，Friedrich Karl Schönborn是Johann Philip Franz于1723年7月12日介绍Pellegrini信件的收件人；该信未在本轮独立查阅。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Schönborn, Friedrich Karl", "S1，S.csv#85"),
            ("脚注姓名", "Friedrich Karl Schönborn", "S3，第10章，p.293 n.4，L560"),
            ("正文姓名形式", "Frederick Karl", "S2，第10章，p.296，L320"),
        ],
        "relation_ids": [
            "st-chp10-p293-note4-franz-schoenborn-letter",
            "st-chp10-p293-note4-franz-letter-addressed-to",
            "st-chp10-p296-bishopric-transfer",
        ],
        "description_zh": (
            "本卡登记书后索引作“Schönborn, Friedrich Karl”、正文另作“Frederick Karl”的第10章人物。"
            "Haskell称其于1746年去世，并叙述Würzburg主教职位经短暂继任期后转归Karl Philip von Greiffenklau；"
            "脚注据Von Freeden将他列为Johann Philip Franz于1723年7月12日介绍Pellegrini信件的收件人。"
            "原信未在本轮独立查阅；以上限于Haskell的叙述。中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the Chapter 10 figure indexed as “Schönborn, Friedrich Karl” and also called “Frederick Karl” in the body. "
            "Haskell places his death in 1746 and says the Würzburg bishopric passed to Karl Philip von Greiffenklau after a short successor interval; "
            "a footnote, citing Von Freeden, identifies him as the addressee of Johann Philip Franz's letter of 12 July 1723 introducing Pellegrini. "
            "The letter was not independently consulted in this work; these details remain limited to Haskell's account. "
            "The Chinese display name is a working transliteration."
        ),
        "context_zh": (
            "涉及本人的三条S2候选涵盖脚注所述信件及其收件人、以及1746年去世后Würzburg主教职位的转移；"
            "原信未读，三条均保留来源限定并待S6裁决。"
        ),
        "context_en": (
            "The three S2 candidates involving him cover the footnoted letter and its addressee, and the transfer of the Würzburg bishopric after his death in 1746. "
            "The letter was not read; all three candidates retain their source limits and remain for S6 review."
        ),
    },
    {
        "candidate": "cand-2398",
        "group": "new-person:franz-johann-philip-schonborn-934e428cde",
        "ku": "units/persons/johann-philip-franz-schonborn",
        "card": "04-knowledge/units/persons/johann-philip-franz-schonborn.md",
        "name_zh": "约翰·菲利普·弗朗茨·申伯恩",
        "name_en": "Johann Philip Franz Schönborn",
        "index_entry": "S.csv#86",
        "index_name": "Schönborn, Johann Philip Franz",
        "index_page": "293n",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "book_sources": [
            book_source(
                "02-sources/02-Markdown/10_CHP-10_intro.md",
                "第10章脚注4，印刷页293，行560",
                "line 560; print p. 293 n. 4",
                "A letter from Johann Philip Franz to Friedrich Karl Schönborn dated 12 July 1723 to introduce Pellegrini speaks of his success in London, Paris and Diisseldorf—Von Freeden, 1955, p. 848.",
                "Haskell脚注据Von Freeden称Johann Philip Franz为1723年7月12日介绍Pellegrini信件的作者；该信未在本轮独立查阅。",
            )
        ],
        "name_rows": [
            ("索引姓名", "Schönborn, Johann Philip Franz", "S1，S.csv#86"),
            ("脚注姓名", "Johann Philip Franz", "S2，第10章，p.293 n.4，L560"),
        ],
        "relation_ids": [
            "st-chp10-p293-note4-franz-schoenborn-letter",
            "st-chp10-p293-note4-franz-letter-authored-by",
        ],
        "description_zh": (
            "本卡登记书后索引作“Schönborn, Johann Philip Franz”的第10章人物。"
            "Haskell脚注据Von Freeden称，他于1723年7月12日致信Friedrich Karl Schönborn介绍Pellegrini，并提及画家在伦敦、巴黎和Düsseldorf的成功。"
            "原信未在本轮独立查阅，身份和信件内容均按Haskell脚注转述记录。中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the Chapter 10 figure indexed as “Schönborn, Johann Philip Franz.” "
            "A Haskell footnote, citing Von Freeden, says that he wrote to Friedrich Karl Schönborn on 12 July 1723 to introduce Pellegrini, "
            "mentioning the painter's success in London, Paris, and Düsseldorf. "
            "The letter was not independently consulted; both the identification and its contents are recorded as Haskell's footnote report. "
            "The Chinese display name is a working transliteration."
        ),
        "context_zh": (
            "同一脚注的综合陈述和作者指认均为S2关系候选；书信原件未读，关系与信件细节待S6依据现有证据裁决。"
        ),
        "context_en": (
            "The combined footnote statement and the author identification are both S2 relation candidates. "
            "The letter itself was not read; the relation and its details remain for S6 review on the available evidence."
        ),
    },
    {
        "candidate": "cand-2399",
        "group": "new-person:franz-lothar-schonborn-von-9635ffd088",
        "ku": "units/persons/lothar-franz-von-schonborn",
        "card": "04-knowledge/units/persons/lothar-franz-von-schonborn.md",
        "name_zh": "洛塔尔·弗朗茨·冯·申伯恩",
        "name_en": "Lothar Franz von Schönborn",
        "index_entry": "S.csv#87",
        "index_name": "Schönborn, Lothar Franz von",
        "index_page": "195",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
        "book_sources": [
            book_source(
                "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "第7章第4节，印刷页195，行40–41",
                "lines 40–41; print p. 195",
                "A generation later Lothar Franz von Schonborn wrote to much the same effect: ‘Une Souzanne et la Pudiphar seroit assez de mon gout; quant a la nudité je ne m’en scandalise pas trop dans les peintures, pourvue quelles ne soit obscène, et qu’il n’y ayet pas des actions ou gesticulations infâmes, et comme j’ay observé que le plus fort de\nStrudel consiste in dem nakenden, allso muss man ihn davon nicht abhallten outre qu’un beau corps et visage de femme orne bien un tableau.’",
                "Haskell称Lothar Franz von Schonborn在信中表示，他偏好Susanna与Potiphar题材，接受不涉淫秽的裸体，并称Strudel擅长裸体形象。",
            ),
            book_source(
                "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "第7章脚注2，印刷页195，行104",
                "line 104; print p. 195 n. 2",
                "Letter of 10 October 1708—Hantsch und Schers, p. 164.",
                "Haskell脚注把相关信件日期标为1708年10月10日，并指向Hantsch und Schers第164页；该书信和所引刊物未在本轮独立查阅。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Schönborn, Lothar Franz von", "S1，S.csv#87"),
            ("正文姓名形式", "Lothar Franz von Schonborn", "S2，第7章，p.195，L40"),
        ],
        "relation_ids": [
            "st-chp7-p195-german-patron-generalization",
            "st-chp7-p195-lothar-schonborn-letter",
            "st-chp7-p195-n2-schoenborn-letter",
        ],
        "description_zh": (
            "本卡登记书后索引作“Schönborn, Lothar Franz von”、正文作“Lothar Franz von Schonborn”的第7章人物。"
            "Haskell引述一封信，其中Lothar称“Une Souzanne et la Pudiphar”颇合其意，并表示绘画可有裸体但不应淫秽或不雅，还评价Strudel擅长裸体形象。"
            "脚注将信件日期标为1708年10月10日并指向Hantsch und Schers第164页；原信及所引刊物未在本轮独立查阅。"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the Chapter 7 figure indexed as “Schönborn, Lothar Franz von” and spelled “Lothar Franz von Schonborn” in the body. "
            "Haskell quotes a letter in which Lothar says that “Une Souzanne et la Pudiphar” would suit his taste, accepts nudity in paintings while excluding obscene or indecent treatment, "
            "and describing Strudel as especially capable with nude figures. "
            "The footnote dates the letter to 10 October 1708 and points to Hantsch und Schers, page 164; neither the letter nor that cited work was independently consulted here. "
            "The Chinese display name is a working transliteration."
        ),
        "context_zh": (
            "相关三条S2候选分别涉及信中陈述、Haskell关于其他德国赞助人的概括，以及脚注书目指引；"
            "后两者不作为独立人物关系或已核实原件处理，均留待S6。"
        ),
        "context_en": (
            "The three related S2 candidates cover the quoted letter, Haskell's generalization about other German patrons, and the footnote's bibliographic pointer. "
            "The latter two are not treated as independent personal relations or as verification of the original letter; all remain for S6."
        ),
    },
]


def make_card(t: dict) -> str:
    sources = [index_source(t), *t["book_sources"]]
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
    rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in t["name_rows"])
    relation_ids = "、".join(sid for sid in t["relation_ids"])
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {t['description_zh']}

**English:** {t['description_en']}

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
{rows}

### 本书相关内容

**中文：** {t['context_zh']}

**English:** {t['context_en']}

## 关系与证据

### 关系记录

当前没有登记在 relations.csv 中的正式关系。S2关系候选 {relation_ids} 保留原书归因和限制，留待S6逐条裁决；本次S4身份登记不将其转为正式关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register four S-index person endpoint groups.")
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
    statements = sync.load_statements()

    for t in TARGETS:
        cid = t["candidate"]
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate.get("suggested_type") == "person"
        assert alignment.get("decision") == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == t["group"]
        group_members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == t["group"]
        ]
        assert group_members == [cid], (t["group"], group_members)
        assert candidate.get("index_entry_id") == t["index_entry"]
        assert candidate.get("canonical_name") == t["index_name"]
        assert candidate.get("index_page_range") == t["index_page"]
        index_rows = person_sync.read_index_rows("S.csv")
        index_row = index_rows[int(t["index_entry"].split("#")[1])]
        assert index_row.get("Main Entry") == t["index_name"]
        assert index_row.get("Page Numbers", "") == t["index_page"]
        body = (ROOT / t["source_file"]).read_text(encoding="utf-8-sig")
        for source in t["book_sources"]:
            assert source["original_quotes"][0]["text"] in body
        assert t["ku"] not in manifest_by_ku
        assert t["card"] not in accepted_paths
        assert not (ROOT / t["card"]).exists()
        assert not any(
            row.get("type") == "person"
            and (row.get("name_en") or "").casefold() == t["name_en"].casefold()
            for row in manifest
        )
        related = {
            row["statement_id"] for row in statements
            if (row.get("qualifiers") or {}).get("relation_candidate") is True
            and (
                cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
                or cid in (row.get("qualifiers") or {}).get("mentioned_candidate_ids", [])
            )
        }
        assert related == set(t["relation_ids"]), (cid, related, set(t["relation_ids"]))

    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    for t in TARGETS:
        row = next(
            row for row in planned_alignments
            if row.get("candidate_id") == t["candidate"] and not row.get("external_source")
        )
        row["ku_id"] = t["ku"]
        row["process_ref"] = PROCESS_REF
        suffix = (
            f" S4登记（{DATE}）：身份组{t['group']}映射至{t['ku']}；"
            "新增一张书内来源支持的人物KU，相关S2关系候选仍待S6。"
        )
        if t["candidate"] in {"cand-2397", "cand-2398"}:
            suffix += "两位Schönborn按各自全名与独立S3身份组分别登记，不因同姓合并。"
        row["resolution_note"] = row.get("resolution_note", "").rstrip() + suffix
        planned_manifest.append({
            "ku_id": t["ku"],
            "type": "person",
            "canonical_name": t["name_zh"],
            "name_en": t["name_en"],
            "source_task": TASK,
            "card_path": t["card"],
        })
    planned_manifest.sort(key=lambda row: row["ku_id"])

    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        planned_accepted = person_sync.insert_accepted(planned_accepted, t["card"])
    assert len({line[2:] for line in planned_accepted if line.startswith("- 04-knowledge/units/")}) == len(accepted_paths) + len(TARGETS)

    baseline = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert stats["person"]["registered_groups"] == baseline["person"]["registered_groups"] + len(TARGETS)
    assert stats["person"]["registered_members"] == baseline["person"]["registered_members"] + len(TARGETS)
    assert stats["person"]["pending_groups"] == baseline["person"]["pending_groups"] - len(TARGETS)
    assert stats["person"]["pending_members"] == baseline["person"]["pending_members"] - len(TARGETS)
    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    cards = {t["card"]: make_card(t) for t in TARGETS}
    for card in cards.values():
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert match and isinstance(yaml.safe_load(match.group(1)), dict)

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    log_rows = []
    for t in TARGETS:
        rels = "、".join(t["relation_ids"])
        log_rows.append(
            f"- {t['candidate']}（{t['group']}）→ [{t['name_zh']}（{t['name_en']}）]"
            f"(../../../{t['card']})；S2关系候选{rels}留待S6。{t['context_zh']}"
        )
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 person：Schmidt与Schönborn四个身份组登记（{DATE}）\n\n"
        + "\n".join(log_rows)
        + "\n\n四条S3 new决定分别对应四个单候选身份组，各登记一张人物KU。"
        "Friedrich Karl与Johann Philip Franz Schönborn按不同全名和独立身份组分别登记。"
        "书信及引文均保留Haskell的转述范围；Johann Philip Franz与Friedrich Karl相关信件原件、"
        "Lothar Franz所引信件及书目均未在本轮独立查阅。"
        "本批不新增外部来源、正式关系或backlog项目。\n\n"
        f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        f"{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/"
        f"{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text += (
        f"\n\n### S4 人物身份组登记：S索引四个直接端点（{DATE}）\n\n"
        + "；".join(
            f"{t['candidate']} → ../units/persons/{t['ku'].split('/')[-1]}.md"
            for t in TARGETS
        )
        + "。四个S3 new单候选身份组各登记一个KU；Schönborn三人按各自全名分别保留。"
        "本批涉及的S2关系候选继续待S6；书信原件与引文依据保留各自核读限制。未新增外部来源或正式关系。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: four singleton person groups; S.csv/source/mentioned-endpoint checks passed; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; person_registered="
            f"{stats['person']['registered_groups']}/{stats['person']['registered_members']}; "
            f"person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; "
            f"KU={len(planned_manifest)}; relation_candidates="
            f"{sum(len(t['relation_ids']) for t in TARGETS)}; external_sources_added=0; "
            "formal_relations_added=0; no files changed"
        )
        return 0

    for rel_path, card in cards.items():
        (ROOT / rel_path).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups=4; candidate_mappings=4; KU={len(planned_manifest)}; "
        f"person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; "
        f"person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; "
        f"relation_candidates={sum(len(t['relation_ids']) for t in TARGETS)}; "
        "external_sources_added=0; formal_relations_added=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
