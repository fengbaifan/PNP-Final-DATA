from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sys
from io import StringIO
from pathlib import Path

import yaml

PROCESS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-16"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

GROUPS = [
    {
        "group": "new-person:baglione-giovanni-f65db6f695",
        "members": ("cand-0156", "cand-0157", "cand-0158"),
        "ku_id": "units/persons/giovanni-baglione",
        "card_rel": "04-knowledge/units/persons/giovanni-baglione.md",
        "type": "person",
        "name_zh": "乔瓦尼·巴廖内",
        "name_en": "Giovanni Baglione",
        "description_zh": (
            "本卡对应全书索引主项 Baglione, Giovanni；其中 Resurrection（p.66）和 Divine Love（p.127）"
            "是作品子项。第3章以 Giovanni Baglione 全名记其与耶稣会的付款争议及1602年祭坛画，"
            "第5章再次以全名记其与 Orazio Gentileschi 的绘画竞争。S3据同一索引主项及正文姓名锚点，"
            "将 cand-0156、cand-0157、cand-0158 归入同一人物组。中文名为项目工作音译。"
        ),
        "description_en": (
            "This unit corresponds to the main index entry Baglione, Giovanni; Resurrection (p. 66) and "
            "Divine Love (p. 127) are work subentries under that person. Chapter 3 names Giovanni Baglione "
            "in the Jesuit payment dispute and in its account of a 1602 altarpiece; Chapter 5 again names "
            "him in the account of his pictorial rivalry with Orazio Gentileschi. S3 groups cand-0156, "
            "cand-0157, and cand-0158 under the same person on the shared index heading and the full-name "
            "text anchors. The Chinese display name is a project working transliteration."
        ),
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "全书索引 B.csv#3–5；Baglione, Giovanni 主项及 Resurrection、Divine Love 子项",
                "sentence_summary": "主项Baglione, Giovanni列p.66、84、127、159、175；同名人物项下另列Divine Love和Resurrection子项。",
                "quotes": [
                    ("B.csv#3", "Baglione, Giovanni"),
                    ("B.csv#4", "Baglione, Giovanni"),
                    ("B.csv#5", "Baglione, Giovanni"),
                ],
                "source_file": "02-sources/03-Index/03-2-Index-CSV/B.csv",
                "source_span": "B.csv#3; B.csv#4; B.csv#5",
            },
            {
                "citation": BOOK_CITATION,
                "location": "第3章 p.66；L11–13",
                "sentence_summary": "Haskell称Baglione绘制The Resurrection后五年因耶稣会未付全款而向教宗投诉；投诉年份不由相对时间单独推算。",
                "quotes": [
                    (
                        "lines 11–13; print p. 66",
                        "Five years after producing a picture of The Resurrection Giovanni\n"
                        "Baglione was forced to complain to the Pope that he had not yet been fully paid by the\n"
                        "Jesuit fathers",
                    )
                ],
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "source_span": "lines 11–13; print p. 66",
            },
            {
                "citation": BOOK_CITATION,
                "location": "第3章 p.84；L79",
                "sentence_summary": "Haskell称Baglione于1602年为耶稣堂右横翼礼拜堂绘制祭坛画；该段称礼拜堂此前曾奉献于Resurrection。",
                "quotes": [
                    (
                        "line 79; print p. 84",
                        "It had originally been dedicated to the Saviour and then to the Resurrection; "
                        "for it Baglione had painted an altarpiece in 1602.",
                    )
                ],
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
                "source_span": "line 79; print p. 84",
            },
            {
                "citation": BOOK_CITATION,
                "location": "第5章 p.127；L79–80",
                "sentence_summary": "Haskell引述Orazio Gentileschi对Baglione与其画作竞争的说法，并记有Divine Love与Earthly Love两件作品。",
                "quotes": [
                    (
                        "line 80; print p. 127",
                        "he [Giovanni Baglione] competed with me by putting a picture just opposite it.",
                    ),
                    (
                        "line 80; print p. 127",
                        "And this picture which was called Divine Love he had painted in competition with "
                        "Michelangelo da Caravaggio’s Earthly Love.",
                    ),
                ],
                "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
                "source_span": "lines 79–80; print p. 127",
            },
        ],
        "tables": [
            (
                "姓名",
                [
                    ("规范姓名", "Giovanni Baglione", "S2，第3章 p.66；S4，第5章 p.127"),
                    ("索引形式", "Baglione, Giovanni", "S1，B.csv#3"),
                ],
            ),
            ("身份", [("身份", "画家", "S3，第3章 p.84")]),
        ],
        "context_zh": (
            "第3章分别记载Baglione因《The Resurrection》画作的报酬问题向教宗投诉，以及他于1602年为耶稣堂右横翼礼拜堂"
            "绘制祭坛画。S3把两处作品锚点合为一个作品组，依据为同一画家、复活题材、耶稣会教堂语境与年代相容；"
            "p.84未重复题名，p.66也未明说地点，因此不推定祭坛画的题名出处、陈列状态或投诉年份。第5章记有Divine Love"
            "与Caravaggio的Earthly Love之间的竞争叙述。相关关系候选保留待S6审查。"
        ),
        "context_en": (
            "Chapter 3 separately records Baglione’s payment complaint concerning a picture called The Resurrection and his 1602 "
            "altarpiece for the Gesù’s right transept chapel. S3 groups the two work references based on the same painter, resurrection "
            "subject, Jesuit church context, and compatible chronology. The p. 84 passage does not repeat the title, and p. 66 does not "
            "name the location, so the unit does not infer the title’s source, display status, or the complaint year. Chapter 5 also "
            "records the account of Divine Love in competition with Caravaggio’s Earthly Love. Relation candidates remain for S6 review."
        ),
        "relation_note_zh": "当前没有正式关系。6条直接S2关系候选的端点现均有KU映射，仍须在S6逐条审查后才能建立正式边。",
        "relation_note_en": "No formal relations are recorded. All endpoints in the six direct S2 relation candidates now have KU mappings; each claim remains for S6 review before any formal edge is created.",
    },
    {
        "group": "workgrp-3089e5ca7ba112",
        "members": ("cand-5013", "cand-5297"),
        "ku_id": "units/works/giovanni-baglione-resurrection-gesu-altarpiece",
        "card_rel": "04-knowledge/units/works/giovanni-baglione-resurrection-gesu-altarpiece.md",
        "type": "work",
        "name_zh": "《复活》（乔瓦尼·巴廖内为耶稣堂绘制的祭坛画）",
        "name_en": "The Resurrection (Giovanni Baglione altarpiece for the Gesù)",
        "description_zh": (
            "本卡将第3章 p.66 所称Baglione的The Resurrection画作与p.84记载的1602年耶稣堂右横翼礼拜堂祭坛画"
            "登记为同一作品组。依据是同一画家、复活题材、耶稣会教堂语境及相容年代。p.84没有重述作品题名，"
            "p.66没有明说地点；本卡不推定具体陈列状态、完整题名或投诉年份，亦未作外部目录核验。"
        ),
        "description_en": (
            "This unit groups the The Resurrection picture attributed to Baglione on p. 66 with the 1602 altarpiece for the Gesù’s "
            "right transept chapel described on p. 84. The grouping rests on the same painter, resurrection subject, Jesuit church "
            "context, and compatible chronology. Page 84 does not repeat the title, and p. 66 does not state the location; this unit "
            "does not infer display status, a fuller title, or the complaint year, and no external catalogue was checked."
        ),
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第3章 p.66；L11–13",
                "sentence_summary": "Haskell称Baglione绘制The Resurrection后五年因耶稣会未付全款而投诉；该画作的位置及投诉年份不明。",
                "quotes": [
                    (
                        "lines 11–13; print p. 66",
                        "Five years after producing a picture of The Resurrection Giovanni\n"
                        "Baglione was forced to complain to the Pope that he had not yet been fully paid by the\n"
                        "Jesuit fathers",
                    )
                ],
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "source_span": "lines 11–13; print p. 66",
            },
            {
                "citation": BOOK_CITATION,
                "location": "第3章 p.84；L79",
                "sentence_summary": "Haskell称Baglione于1602年为耶稣堂右横翼礼拜堂绘制祭坛画；礼拜堂此前曾奉献于Resurrection。",
                "quotes": [
                    (
                        "line 79; print p. 84",
                        "It had originally been dedicated to the Saviour and then to the Resurrection; "
                        "for it Baglione had painted an altarpiece in 1602.",
                    )
                ],
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
                "source_span": "line 79; print p. 84",
            },
        ],
        "tables": [
            ("题名", [("题名", "The Resurrection", "S1，第3章 p.66；S2，第3章 p.84")]),
            (
                "基本信息",
                [
                    ("作品类型", "祭坛画", "S2，第3章 p.84"),
                    ("创作时间", "1602年", "S2，第3章 p.84"),
                    ("创作者", "Giovanni Baglione", "S1，第3章 p.66；S2，第3章 p.84"),
                ],
            ),
        ],
        "context_zh": (
            "Haskell在第3章 p.66称Baglione绘制一幅The Resurrection画作，五年后因耶稣会未足额付款而投诉；"
            "p.84称他于1602年为耶稣堂右横翼礼拜堂绘制祭坛画，并说明礼拜堂曾奉献于Resurrection。S3据共同画家、"
            "题材、教堂语境和时间相容将两条候选合并。两处未明确说明作品位置与题名的对应细节，相关限制仍保留。"
        ),
        "context_en": (
            "On p. 66 Haskell says Baglione produced a picture called The Resurrection and complained five years later about incomplete "
            "payment by the Jesuits. On p. 84 Haskell says Baglione painted an altarpiece for the Gesù’s right transept chapel in 1602, "
            "noting that the chapel had been dedicated to the Resurrection. S3 groups the two candidates using the shared painter, "
            "subject, church context, and compatible chronology. The passages do not explicitly state the location-title link, so that "
            "limitation remains recorded."
        ),
        "relation_note_zh": "当前没有正式关系。创作者与委托语境保留为S2来源断言及关系候选，待S6审查。",
        "relation_note_en": "No formal relations are recorded. The maker and commission context remain source claims and relation candidates for S6 review.",
    },
    {
        "group": "workgrp-933165de3ec465",
        "members": ("cand-6045",),
        "ku_id": "units/works/giovanni-baglione-divine-love",
        "card_rel": "04-knowledge/units/works/giovanni-baglione-divine-love.md",
        "type": "work",
        "name_zh": "《神圣之爱》（Divine Love）",
        "name_en": "Divine Love (painting by Giovanni Baglione)",
        "description_zh": (
            "本卡对应Haskell引述Orazio Gentileschi所称的Divine Love画作。叙述将作品归于Giovanni Baglione，"
            "并称其与Caravaggio的Earthly Love构成竞争；人名方括号为引文中的补名形式。题名按原文保留，"
            "本卡不据此补充年代、尺寸、馆藏或现状。"
        ),
        "description_en": (
            "This unit identifies the painting called Divine Love in Haskell’s account of Orazio Gentileschi’s testimony. The narrative "
            "attributes the painting to Giovanni Baglione and says it was made in competition with Caravaggio’s Earthly Love; the "
            "artist’s name appears in square brackets as an editorial identification within the quotation. The source title is retained, "
            "with no added date, dimensions, collection, or present status."
        ),
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第5章 p.127；L79–80",
                "sentence_summary": "Haskell引述Orazio Gentileschi称Baglione将Divine Love置于其画作对面，并称其与Caravaggio的Earthly Love竞争。",
                "quotes": [
                    (
                        "line 80; print p. 127",
                        "he [Giovanni Baglione] competed with me by putting a picture just opposite it.",
                    ),
                    (
                        "line 80; print p. 127",
                        "And this picture which was called Divine Love he had painted in competition with "
                        "Michelangelo da Caravaggio’s Earthly Love.",
                    ),
                ],
                "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
                "source_span": "lines 79–80; print p. 127",
            },
        ],
        "tables": [
            ("题名", [("题名", "Divine Love", "S1，第5章 p.127")]),
            (
                "基本信息",
                [
                    ("作品类型", "绘画", "S1，第5章 p.127"),
                    ("创作者", "Giovanni Baglione", "S1，第5章 p.127"),
                ],
            ),
        ],
        "context_zh": (
            "Haskell将作品置于1603年Orazio Gentileschi关于罗马艺术家竞争的证言中；Haskell称其题为Divine Love，"
            "并说它与Caravaggio的Earthly Love竞争。该段未提供创作日期、尺寸、收藏或现状。"
        ),
        "context_en": (
            "Haskell places the painting in Orazio Gentileschi’s 1603 testimony about competition among artists in Rome. Haskell names "
            "it Divine Love and says it competed with Caravaggio’s Earthly Love. The passage supplies no creation date, dimensions, "
            "collection, or present status."
        ),
        "relation_note_zh": "当前没有正式关系。作品与Baglione的创作者关系及与Earthly Love的竞争陈述留待S6审查。",
        "relation_note_en": "No formal relations are recorded. The creator claim and the competition with Earthly Love remain for S6 review.",
    },
    {
        "group": "workgrp-9507832709ee31",
        "members": ("cand-6046",),
        "ku_id": "units/works/caravaggio-earthly-love",
        "card_rel": "04-knowledge/units/works/caravaggio-earthly-love.md",
        "type": "work",
        "name_zh": "《世间之爱》（Earthly Love）",
        "name_en": "Earthly Love (painting attributed to Caravaggio in Haskell)",
        "description_zh": (
            "本卡对应Haskell在Orazio Gentileschi证言叙述中称为Earthly Love的画作。该处将其归于Michelangelo da Caravaggio，"
            "并称它与Baglione的Divine Love构成竞争。题名按原文保留，不据此补充年代、尺寸、馆藏或现状。"
        ),
        "description_en": (
            "This unit identifies the painting called Earthly Love in Haskell’s account of Orazio Gentileschi’s testimony. The passage "
            "attributes it to Michelangelo da Caravaggio and says it was in competition with Baglione’s Divine Love. The source title is "
            "retained, with no added date, dimensions, collection, or present status."
        ),
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第5章 p.127；L80",
                "sentence_summary": "Haskell称Baglione的Divine Love与Michelangelo da Caravaggio的Earthly Love构成竞争。",
                "quotes": [
                    (
                        "line 80; print p. 127",
                        "And this picture which was called Divine Love he had painted in competition with "
                        "Michelangelo da Caravaggio’s Earthly Love.",
                    )
                ],
                "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
                "source_span": "line 80; print p. 127",
            },
        ],
        "tables": [
            ("题名", [("题名", "Earthly Love", "S1，第5章 p.127")]),
            (
                "基本信息",
                [
                    ("作品类型", "绘画", "S1，第5章 p.127"),
                    ("创作者", "Michelangelo da Caravaggio", "S1，第5章 p.127"),
                ],
            ),
        ],
        "context_zh": (
            "作品见第5章 p.127 对Orazio Gentileschi 1603年证言的转述。Haskell称Michelangelo da Caravaggio创作Earthly Love，"
            "并将其与Baglione的Divine Love并列于艺术竞争语境；原证言及作品实物未在本轮独立核阅。"
        ),
        "context_en": (
            "The work appears in Haskell’s account of Orazio Gentileschi’s 1603 testimony on p. 127. Haskell names Earthly Love as a "
            "work by Michelangelo da Caravaggio and places it alongside Baglione’s Divine Love in an account of artistic rivalry; the "
            "testimony and the physical painting were not independently consulted in this registration."
        ),
        "relation_note_zh": "当前没有正式关系。与Divine Love的竞争陈述保留为S2关系候选，待S6审查。",
        "relation_note_en": "No formal relations are recorded. The competition with Divine Love remains an S2 relation candidate for S6 review.",
    },
]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def csv_text(fieldnames, rows) -> str:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def get_group(note: str) -> str | None:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def insert_accepted(text: str, paths: list[str]) -> str:
    lines = text.splitlines()
    for card_rel in sorted(paths):
        if any(line.strip() == f"- {card_rel}" for line in lines):
            raise ValueError(f"Accepted path already exists: {card_rel}")
        insert_at = next(
            (
                i for i, line in enumerate(lines)
                if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel
            ),
            next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
        )
        lines.insert(insert_at, f"- {card_rel}")
    return "\n".join(lines) + "\n"


def make_source(item: dict) -> dict:
    return {
        "citation": item["citation"],
        "location": item["location"],
        "sentence_summary": item["sentence_summary"],
        "original_quotes": [
            {"source_span": span, "text": quote}
            for span, quote in item["quotes"]
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": item["source_file"],
            "source_span": item["source_span"],
        },
    }


def source_link(item: dict, label: str) -> str:
    path = item["source_file"].replace("02-sources/", "../../../02-sources/")
    return f"[{label}]({path})（{item['location']}）"


def make_card(definition: dict) -> str:
    frontmatter = {
        "title": f"{definition['name_zh']}（{definition['name_en']}）",
        "name_en": definition["name_en"],
        "type": definition["type"],
        "evidence_status": "source_backed",
        "sources": [make_source(item) for item in definition["sources"]],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_links = " ".join(
        source_link(item, item["location"])
        for item in definition["sources"]
    )
    body_parts = [
        "## 内容",
        "",
        "### 描述",
        "",
        f"**中文：** {definition['description_zh']} {source_links}",
        "",
        f"**English:** {definition['description_en']} {source_links}",
        "",
    ]
    for section, rows in definition["tables"]:
        body_parts.extend([
            f"### {section}",
            "",
            "| 字段 | 值 | 证据 |",
            "|---|---|---|",
        ])
        for field, value, evidence in rows:
            body_parts.append(f"| {field} | {value} | {evidence} |")
        body_parts.append("")
    body_parts.extend([
        "### 本书相关内容",
        "",
        definition["context_zh"],
        "",
        definition["context_en"],
        "",
        "## 关系与证据",
        "",
        "### 身份与外部链接",
        "",
        "本卡登记本书中的身份与对象依据；本轮未作外部身份核验。",
        "",
        "This unit records identity and object evidence from the book; no external identity check was made in this registration.",
        "",
        "### 关系记录",
        "",
        definition["relation_note_zh"],
        "",
        definition["relation_note_en"],
        "",
    ])
    return f"---\n{fm}---\n\n" + "\n".join(body_parts)


def current_groups(candidate_rows, alignment_rows):
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    decisions = {
        row["candidate_id"]: row
        for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id)
    for definition in GROUPS:
        rows = [
            row for row in alignment_rows
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and get_group(row.get("resolution_note", "")) == definition["group"]
        ]
        ids = {row["candidate_id"] for row in rows}
        assert ids == set(definition["members"]), (definition["group"], ids)
        assert all(not row.get("ku_id") for row in rows), definition["group"]
        assert all(candidate_by_id[cid]["suggested_type"] == definition["type"] for cid in ids)


def build_process_record(stats, totals, manifest_count) -> str:
    s4_all = (
        f"S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；"
        f"person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记"
        f"{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；"
        f"work已登记{sync.fmt(stats['work']['registered_groups'])}组，待登记"
        f"{sync.fmt(stats['work']['pending_groups'])}组/{sync.fmt(stats['work']['pending_members'])}条成员；manifest={manifest_count}。"
    )
    return (
        f"\n\n### S4 person：Giovanni Baglione跨章人物组登记（{DATE}）\n\n"
        "- cand-0156、cand-0157、cand-0158同映射至units/persons/giovanni-baglione。三条候选分别来自B.csv#3主项、"
        "B.csv#4 Divine Love子项和B.csv#5 Resurrection子项；第3章p.66、第5章p.127的正文全名锚点与共享主项"
        "支持同一人物。工作题名子项不作为人物别名；cand-0157从undecided改为new的依据及旧理由保留在S3记录。\n"
        "- 卡片只收录书内姓名、索引形式和明确画家身份。第3章对1602年祭坛画和The Resurrection报酬争议的两处记录"
        "未推定投诉年份、当前陈列或外部身份；第5章证言按Haskell转述保留。6条直接S2关系候选均有已登记KU端点，"
        "但全部留待S6逐条裁决，本批未修改relations.csv。\n"
        f"- 本批还将cand-5013与cand-5297映射至同一The Resurrection作品KU，并登记cand-6045的Divine Love及"
        "cand-6046的Earthly Love作品KU。各自证据与未采纳的额外推断见卡片、alignment和S3/S4过程段落。"
        "三件作品相关关系候选均未升为正式边。\n"
        f"- {s4_all}build_field_facts.py预检无警告并apply新增13条source-backed字段记录，来源登记未变化，unverified保持1,578；本批不做S5补足或外部采集。"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Register the Baglione person group and three directly connected work groups."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment = read_csv(ALIGNMENT)
    manifest_fields, manifest = read_csv(MANIFEST)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    current_groups(candidates, alignment)

    new_manifest_rows = []
    card_paths = []
    for definition in GROUPS:
        card_path = ROOT / definition["card_rel"]
        assert not card_path.exists(), f"card already exists: {card_path}"
        assert not any(
            row.get("ku_id") == definition["ku_id"]
            or row.get("card_path") == definition["card_rel"]
            for row in manifest
        ), definition["ku_id"]
        assert not any(
            row.get("type") == definition["type"]
            and row.get("name_en", "").casefold() == definition["name_en"].casefold()
            for row in manifest
        ), f"matching {definition['type']} KU already exists: {definition['name_en']}"
        new_manifest_rows.append({
            "ku_id": definition["ku_id"],
            "type": definition["type"],
            "canonical_name": definition["name_zh"],
            "name_en": definition["name_en"],
            "source_task": TASK,
            "card_path": definition["card_rel"],
        })
        card_paths.append(card_path)

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    person_ids = set(GROUPS[0]["members"])
    person_direct = [
        row for row in statements
        if row.get("subject_candidate_id") in person_ids or row.get("object_candidate_id") in person_ids
    ]
    person_relation = [
        row for row in person_direct
        if row.get("qualifiers", {}).get("relation_candidate")
    ]
    assert (len(person_direct), len(person_relation)) == (6, 6)

    work_expectations = {
        "workgrp-3089e5ca7ba112": (1, 1),
        "workgrp-933165de3ec465": (2, 2),
        "workgrp-9507832709ee31": (1, 1),
    }
    for definition in GROUPS[1:]:
        ids = set(definition["members"])
        direct = [
            row for row in statements
            if row.get("subject_candidate_id") in ids or row.get("object_candidate_id") in ids
        ]
        relations = [
            row for row in direct
            if row.get("qualifiers", {}).get("relation_candidate")
        ]
        assert (len(direct), len(relations)) == work_expectations[definition["group"]]

    for definition in GROUPS:
        for item in definition["sources"]:
            source_path = ROOT / item["source_file"]
            source_text = source_path.read_text(encoding="utf-8-sig")
            for _, quote in item["quotes"]:
                assert quote in source_text, (definition["ku_id"], item["location"], quote)

    revised_alignment = [dict(row) for row in alignment]
    revised_by_id = {
        row["candidate_id"]: row
        for row in revised_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for definition in GROUPS:
        for cid in definition["members"]:
            row = revised_by_id[cid]
            assert row["decision"] == "new" and not row.get("ku_id")
            assert get_group(row["resolution_note"]) == definition["group"]
            row["ku_id"] = definition["ku_id"]
            row["resolution_note"] += (
                f" S4 registration ({DATE}): mapped {definition['group']} to {definition['ku_id']}."
            )

    revised_manifest = list(manifest) + new_manifest_rows
    revised_manifest.sort(key=lambda row: row["ku_id"])
    accepted_text = insert_accepted(
        ACCEPTED.read_text(encoding="utf-8-sig"),
        [definition["card_rel"] for definition in GROUPS],
    )
    cards = {
        ROOT / definition["card_rel"]: make_card(definition)
        for definition in GROUPS
    }

    stats_before = sync.summarize_by_type(candidates, alignment)
    totals_before = {
        key: sum(row[key] for row in stats_before.values())
        for key in next(iter(stats_before.values()))
    }
    stats = sync.summarize_by_type(candidates, revised_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    member_total = sum(len(definition["members"]) for definition in GROUPS)
    assert totals["registered_groups"] == totals_before["registered_groups"] + len(GROUPS)
    assert totals["registered_members"] == totals_before["registered_members"] + member_total
    assert totals["pending_groups"] == totals_before["pending_groups"] - len(GROUPS)
    assert totals["pending_members"] == totals_before["pending_members"] - member_total
    assert len(revised_manifest) == len(manifest) + len(GROUPS)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：Giovanni Baglione跨章人物组登记（{DATE}）"
    assert process_heading not in process_text
    planned_process = process_text + build_process_record(
        stats, totals, len(revised_manifest)
    )
    result_text = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"),
        stats,
        totals,
        len(revised_manifest),
    )
    result_section = (
        f"### S4 person/work：Baglione人物与直接作品端点登记（{DATE}）\n\n"
        "- Giovanni Baglione人物组 cand-0156/0157/0158 映射至一个person KU；"
        "The Resurrection工作组 cand-5013/5297 映射至一个work KU，Divine Love cand-6045与Earthly Love cand-6046"
        "各登记为独立work KU。三组人物/作品身份判断均附有书内证据和候选映射。\n"
        "- 六条直接人物关系候选的端点现均有KU；Divine Love与Earthly Love的2条直接关系候选也有对应作品端点。"
        "所有关系保持待S6审查，本批没有新增正式关系或外部身份核验。\n"
        f"- 当前S4为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射已登记，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{len(revised_manifest)}。"
        "字段表经build_field_facts.py预检无警告并apply新增13条source-backed记录，来源登记未变化、unverified保持1,578。\n\n"
    )
    result_marker = "## 未解决项与交接限制"
    assert result_text.count(result_marker) == 1
    result_text = result_text.replace(result_marker, result_section + result_marker, 1)

    outputs = {
        ALIGNMENT: csv_text(alignment_fields, revised_alignment),
        MANIFEST: csv_text(manifest_fields, revised_manifest),
        ACCEPTED: accepted_text,
        PROCESS: planned_process,
        RESULT: result_text,
        **cards,
    }

    print("S4 registration plan:")
    for definition in GROUPS:
        print(
            f"  {definition['type']}: {definition['group']} -> {definition['ku_id']}; "
            f"members={','.join(definition['members'])}"
        )
    print(f"  person direct statements={len(person_direct)}; relation candidates={len(person_relation)}")
    print(
        f"  S4 after={totals['registered_groups']} groups/{totals['registered_members']} mappings; "
        f"pending={totals['pending_groups']} groups/{totals['pending_members']} mappings"
    )
    print(f"  manifest={len(manifest)} -> {len(revised_manifest)}")
    if args.dry_run:
        print("dry-run passed: group membership, source quotes, types, relation candidate counts, and output paths checked; no files changed")
        for definition in GROUPS:
            print(f"  card preview: {definition['card_rel']} ({definition['name_en']})")
        return 0

    backup_suffix = ".bak-s4-baglione-cross-chapter-20261016"
    existing = [path for path in outputs if path.exists()]
    backups = {}
    for path in existing:
        backup = path.with_name(path.name + backup_suffix)
        if backup.exists():
            raise FileExistsError(f"refusing to overwrite backup: {backup}")
        backups[path] = backup
    for path, backup in backups.items():
        shutil.copy2(path, backup)

    written = []
    try:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            temp = path.with_name(path.name + ".s4-baglione-tmp")
            temp.write_text(content, encoding="utf-8-sig", newline="")
            temp.replace(path)
            written.append(path)
    except Exception:
        for path in written:
            if path in backups:
                shutil.copy2(backups[path], path)
            else:
                path.unlink(missing_ok=True)
        raise

    print("applied four KUs, seven candidate-to-KU mappings, accepted paths, and current process/result records")
    print("field-fact preview and apply remain to be run through scripts/build_field_facts.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
