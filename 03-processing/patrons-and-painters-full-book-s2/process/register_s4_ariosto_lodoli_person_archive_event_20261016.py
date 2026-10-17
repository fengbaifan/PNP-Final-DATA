from __future__ import annotations

import argparse
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
TRECCANI = "https://www.treccani.it/enciclopedia/ludovico-ariosto/"

ITEMS = (
    {
        "candidate": "cand-0116",
        "group": "sg3-person-ludovico-ariosto",
        "ku_id": "units/persons/ludovico-ariosto",
        "card": "04-knowledge/units/persons/ludovico-ariosto.md",
        "type": "person",
        "zh": "卢多维科·阿里奥斯托",
        "en": "Ludovico Ariosto",
    },
    {
        "candidate": "cand-1413",
        "group": "sg3-archive-lodoli-apologhi-1787",
        "ku_id": "units/archives/lodoli-apologhi-1787",
        "card": "04-knowledge/units/archives/lodoli-apologhi-1787.md",
        "type": "archive",
        "zh": "洛多利《Apologhi》1787年版",
        "en": "1787 edition of Lodoli’s Apologhi immaginati",
    },
    {
        "candidate": "cand-1651",
        "group": "sg3-event-publication-lodoli-apologhi-1787",
        "ku_id": "units/events/memmo-apologhi-publication-1787",
        "card": "04-knowledge/units/events/memmo-apologhi-publication-1787.md",
        "type": "event",
        "zh": "梅莫就任时《Apologhi》出版事件（1787）",
        "en": "1787 publication of Lodoli’s Apologhi for Memmo’s assumption of office",
    },
)


def frontmatter(item: dict, sources: list[dict]) -> str:
    data = {
        "title": f"{item['zh']}（{item['en']}）",
        "name_en": item["en"],
        "type": item["type"],
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)


def book_source(location: str, summary: str, file: str, span: str, quotes: list[tuple[str, str]]) -> dict:
    return {
        "citation": BOOK,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": qspan, "text": quote} for qspan, quote in quotes],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": file, "source_span": span},
    }


def person_card(item: dict) -> str:
    sources = [
        book_source(
            "第4章，印刷页103；OCR L47",
            "Haskell转述Galileo讨论Tasso与其喜爱的Ariosto。",
            "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
            "lines 47; print p. 103",
            [("lines 47", "his own favourite Ariosto")],
        ),
        book_source(
            "第9章，印刷页258；OCR L182",
            "Haskell将Ariosto列为Valmarana别墅壁画所表现的文学来源之一。",
            "02-sources/02-Markdown/09_CHP-9_intro.md",
            "lines 182–183; print p. 258",
            [("lines 182", "romantic scenes from Homer, Virgil, Tasso and Ariosto")],
        ),
        book_source(
            "第13章，印刷页339；OCR L75",
            "Haskell称Zatta出版意大利经典时列有Ariosto，未在该句指定单一作品版本。",
            "02-sources/02-Markdown/13_CHP-13_intro.md",
            "lines 75; print p. 339",
            [("lines 75", "some years later Ariosto, Tasso and Metastasio")],
        ),
        book_source(
            "第20章后记，印刷页405；OCR L142–144",
            "Haskell转述Puppi关于Valmarana壁画委托者的更正，并以Ariosto等文学题材指称该组壁画。",
            "02-sources/02-Markdown/20_CHP-20Postscript.md",
            "lines 142–144; print p. 405",
            [("lines 142–143", "illustrating scenes from Homer, Virgil, Ariosto and Tasso")],
        ),
        {
            "citation": f'Treccani, “Ariòsto, Ludovico,” Enciclopedia on line. {TRECCANI}. Accessed 2026-10-16.',
            "location": "词条标题、开篇身份段及“Vita e opere”",
            "sentence_summary": "规范姓名为Ludovico Ariosto；条目称其为诗人，并将Orlando furioso列为其作品。",
        },
    ]
    fm = frontmatter(item, sources)
    p4 = "[第4章 p.103](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md)（L47）"
    p9 = "[第9章 p.258](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L182–183）"
    p13 = "[第13章 p.339](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L75）"
    p20 = "[第20章后记 p.405](../../../02-sources/02-Markdown/20_CHP-20Postscript.md)（L142–144）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应意大利诗人卢多维科·阿里奥斯托。哈斯克尔在不同章节分别于伽利略关于诗与绘画的讨论、提埃波罗 Valmarana 壁画的文学题材，以及 Zatta 出版意大利经典的语境中提及 Ariosto；这些提及归于同一人物。人物姓名按 Treccani 规范为 Ludovico Ariosto；具体文学作品与出版版本仍各自识别，不并入人物卡。{p4}；{p9}；{p13}；{p20}

**English:** This unit represents the Italian poet Ludovico Ariosto. Haskell refers to Ariosto in separate chapters in connection with Galileo’s discussion of poetry and painting, the literary subjects of Tiepolo’s Valmarana frescoes, and Zatta’s editions of Italian classics. These references identify one person. Treccani gives the normalized name Ludovico Ariosto; individual literary works and editions remain separate from the person. {p4}; {p9}; {p13}; {p20}

### 名称与身份

- 规范名：Ludovico Ariosto／卢多维科·阿里奥斯托。Treccani 规范姓名；第4、9、13、20章跨章语境。
- 本书简称：Ariosto。S1及第4、9、13、20章正文。
- 中文名性质：工作音译。项目命名。

### 本书语境

跨章提及覆盖第4、9、13、20章。第4章将 Ariosto 置于 Galileo 转述的文学比较中；第9章与第20章后记提及其文学题材；第13章在 Zatta 出版意大利经典的语境中提及 Ariosto。书中各处不都指定具体作品或版本，不据此生成作品清单。{p4}；{p9}；{p13}；{p20}

## 关系与证据

### 身份与外部链接

[Treccani：Ariòsto, Ludovico](<{TRECCANI}>)（用于人物姓名与作者身份对齐；本链接不表示本书全部陈述均已外部核实）

### 关系记录

当前没有已登记的正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def archive_card(item: dict) -> str:
    file = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
    sources = [
        book_source(
            "第15章，印刷页367；OCR L32",
            "Haskell称Memmo于1787年返威尼斯就任后，出版Lodoli的五十八则Apologhi以纪念其就任。",
            file,
            "lines 32; print p. 367",
            [("lines 32", "To celebrate his official assumption of office he published fifty-eight of Lodoli’s Apologhi—a series of incisive fables which satirised many of the leading figures of Venetian society.")],
        ),
        book_source(
            "第15章，印刷页367；OCR L94，注2",
            "脚注给出印本所列全题名、Lodoli责任者、Bassano [Remondini]及1787年出版项；依S2扫描页校读，OCR“Procurala”更正为印本“Procuratia”。",
            file,
            "lines 94; print p. 367, note 2",
            [("lines 94", "Apologhi immaginati, e sol estemporaneamente in voce esposti agli amici suoi dal Fu Carlo de’ Conti Lodoli Min. Osservante di S. Francesco, facilmente utili all’onesta Gioventù, ed ora per la prima volta pubblicati nell'occasione del Solenne Ingresso che fa alla Procuratia di S. Marco l’eccellentissimo Signor Andrea Memmo, Cavaliere della Stola d’Oro. Bassano [Remondini], 1787.")],
        ),
    ]
    fm = frontmatter(item, sources)
    pbody = "[第15章 p.367](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)（L32）"
    pnote = "[第15章 p.367 注2](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)（L94）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应 Haskell 第15章注2所列的 Carlo de’ Conti Lodoli《Apologhi》1787年版。正文称 Andrea Memmo 为纪念其就任 Procuratore di San Marco 而出版了五十八则寓言，并将其概述为讽刺威尼斯社会人物的短篇。卡片记录的是书中所引书目身份；所引印本未在本轮独立查阅。{pbody}；{pnote}

**English:** This unit identifies the 1787 edition of Carlo de’ Conti Lodoli’s *Apologhi* listed in Haskell’s chapter 15 note 2. The text says Andrea Memmo published fifty-eight fables to mark his assumption of the Procuratore di San Marco office and describes them as satirizing leading figures in Venetian society. This card records the bibliographic identity cited in the book; the cited edition was not independently consulted in this pass. {pbody}; {pnote}

### 题名

- 原题名：*Apologhi immaginati, e sol estemporaneamente in voce esposti agli amici suoi dal Fu Carlo de’ Conti Lodoli Min. Osservante di S. Francesco, facilmente utili all’onesta Gioventù, ed ora per la prima volta pubblicati nell'occasione del Solenne Ingresso che fa alla Procuratia di S. Marco l’eccellentissimo Signor Andrea Memmo, Cavaliere della Stola d’Oro*。{pnote}；S2依据扫描页校读 OCR “Procurala” 为印本 “Procuratia”。
- 中文题名性质：描述性工作译名；保留原题名，不声称为正式中译。项目命名。

### 书目信息

- 文献类型：1787年印本。{pnote}
- 作者：Carlo de’ Conti Lodoli。{pnote}
- 出版地：Bassano。{pnote}
- 出版者：[Remondini]。{pnote}
- 出版年：1787。{pnote}
- 内容说明：Haskell称含五十八则寓言，并称其讽刺威尼斯社会人物；所引印本未独立查阅。{pbody}

## 关系与证据

### 关系记录

当前没有已登记的正式关系。出版责任与出版事件候选依现有 S2 证据留待 S6 审查。
"""
    return f"---\n{fm}---\n\n{body}"


def event_card(item: dict) -> str:
    file = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
    sources = [
        book_source(
            "第15章，印刷页367；OCR L32",
            "Haskell称Memmo于1787年返威尼斯就任 Procuratore di San Marco 后，为纪念就任而出版Lodoli的五十八则寓言。",
            file,
            "lines 32; print p. 367",
            [("lines 32", "In 1787 he returned to Venice to take up the post of Procuratore di San Marco to which he had been appointed two years earlier. To celebrate his official assumption of office he published fifty-eight of Lodoli’s Apologhi.")],
        ),
        book_source(
            "第15章，印刷页367；OCR L94，注2",
            "脚注将该印本题名与出版项系于Memmo的 solemn ingress，并给出Bassano [Remondini]、1787年。",
            file,
            "lines 94; print p. 367, note 2",
            [("lines 94", "ed ora per la prima volta pubblicati nell'occasione del Solenne Ingresso che fa alla Procuratia di S. Marco l’eccellentissimo Signor Andrea Memmo, Cavaliere della Stola d’Oro. Bassano [Remondini], 1787.")],
        ),
    ]
    fm = frontmatter(item, sources)
    pbody = "[第15章 p.367](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)（L32）"
    pnote = "[第15章 p.367 注2](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)（L94）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录 Andrea Memmo 于1787年就任 Procuratore di San Marco 时，为纪念就职而安排出版 Lodoli《Apologhi》的事件。Haskell称该书含五十八则寓言；出版项记于 Bassano [Remondini]，但原文没有将就职仪式地点与印本出版地等同。{pbody}；{pnote}

**English:** This unit records the publication of Lodoli’s *Apologhi* in 1787 on the occasion of Andrea Memmo’s assumption of the Procuratore di San Marco office. Haskell says the book contained fifty-eight fables. The imprint gives Bassano [Remondini], but the passage does not equate the location of the official ceremony with the place of publication. {pbody}; {pnote}

### 事件性质与时间

- 事件性质：Lodoli《Apologhi》出版；与印本 archive KU 分开。{pbody}；{pnote}
- 时间：1787年；原文未给月日。{pbody}；{pnote}
- 就任语境：Memmo返回威尼斯接任 Procuratore di San Marco；Haskell称其为纪念就职而出版。{pbody}
- 出版项：Bassano [Remondini]，1787；此为印本书目地点，不等同于就职活动地点。{pnote}
- 结果：Haskell称出版五十八则寓言，概述为讽刺威尼斯社会人物。{pbody}

## 关系与证据

### 关系记录

当前没有已登记的正式关系。与 Lodoli《Apologhi》印本及 Memmo 的角色关系仍按 S6 核对正式端点和证据。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Ariosto, the Apologhi 1787 edition, and its publication event in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_rows = sync.read_csv(TABLES / "entity-candidates.csv")[1]
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    builders = {"person": person_card, "archive": archive_card, "event": event_card}
    cards = []

    assert len(ITEMS) == 3
    for item in ITEMS:
        cid = item["candidate"]
        candidate = candidates[cid]
        row = decisions[cid]
        assert candidate["suggested_type"] == item["type"]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert sync.get_group(row.get("resolution_note", "")) == item["group"]
        group_rows = [
            r for r in alignments
            if r.get("candidate_id") and not r.get("external_source")
            and r.get("decision") == "new"
            and sync.get_group(r.get("resolution_note", "")) == item["group"]
        ]
        assert [r["candidate_id"] for r in group_rows] == [cid]
        assert not (ROOT / item["card"]).exists()
        assert item["card"] not in accepted
        assert not any(r.get("ku_id") == item["ku_id"] or r.get("card_path") == item["card"] for r in manifest)
        cards.append((ROOT / item["card"], builders[item["type"]](item)))

    source_checks = {
        "02-sources/02-Markdown/04_CHP-4_sec_ii.md": ["his own favourite Ariosto"],
        "02-sources/02-Markdown/09_CHP-9_intro.md": ["romantic scenes from Homer, Virgil, Tasso and Ariosto"],
        "02-sources/02-Markdown/13_CHP-13_intro.md": ["some years later Ariosto, Tasso and Metastasio"],
        "02-sources/02-Markdown/20_CHP-20Postscript.md": ["illustrating scenes from Homer, Virgil, Ariosto and Tasso"],
        "02-sources/02-Markdown/15_CHP-15_sec_ii.md": [
            "To celebrate his official assumption of office he published fifty-eight of Lodoli’s Apologhi",
            "Apologhi immaginati, e sol estemporaneamente in voce esposti agli amici suoi",
            "Bassano [Remondini], 1787",
        ],
    }
    for rel, quotes in source_checks.items():
        text = " ".join((ROOT / rel).read_text(encoding="utf-8-sig").split())
        for quote in quotes:
            assert " ".join(quote.split()) in text, (rel, quote)

    statements = sync.load_statements()
    direct = {}
    for item in ITEMS:
        cid = item["candidate"]
        rows = [r for r in statements if r.get("subject_candidate_id") == cid or r.get("object_candidate_id") == cid]
        direct[cid] = (len(rows), sum(bool(r.get("qualifiers", {}).get("relation_candidate")) for r in rows))

    planned_alignment = [dict(row) for row in alignments]
    alignment_by_id = {
        row["candidate_id"]: row
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_manifest = list(manifest)
    for item in ITEMS:
        row = alignment_by_id[item["candidate"]]
        row["ku_id"] = item["ku_id"]
        row["resolution_note"] += f" S4 registration: mapped {item['group']} to {item['ku_id']}."
        planned_manifest.append({
            "ku_id": item["ku_id"],
            "type": item["type"],
            "canonical_name": item["zh"],
            "name_en": item["en"],
            "source_task": TASK,
            "card_path": item["card"],
        })

    stats = sync.summarize_by_type(candidate_rows, planned_alignment)
    totals = {key: sum(value[key] for value in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S4 person/archive/event：Ariosto 与 Lodoli《Apologhi》出版组登记（2026-10-16）\n\n"
        "`cand-0116` 登记至[卢多维科·阿里奥斯托人物卡](../../../04-knowledge/units/persons/ludovico-ariosto.md)，依据第4、9、13、20章的同一人物语境及 Treccani 规范姓名；不把文学作品、版本并入人物。"
        "`cand-1413` 登记至[《Apologhi》1787年版档案卡](../../../04-knowledge/units/archives/lodoli-apologhi-1787.md)；身份和印次依据 p.367 注2及正文，所引印本未独立查阅。"
        "`cand-1651` 登记至[1787年出版事件卡](../../../04-knowledge/units/events/memmo-apologhi-publication-1787.md)；出版事件与 archive 印本分开，未把出版地 Bassano 当作就职仪式地点。脚注 OCR “Procurala”已依 S2 扫描页校读为印本 “Procuratia”。"
        f"三组直接 S2 断言端点数分别为 {direct['cand-0116'][0]}、{direct['cand-1413'][0]}、{direct['cand-1651'][0]}；archive 与 event 两组共 {direct['cand-1413'][1] + direct['cand-1651'][1]} 条关系候选，均留待 S6。未登记正式关系或开展 S5。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    result_text += (
        "\n\n### S4 person/archive/event：Ariosto 与 Lodoli《Apologhi》出版组登记（2026-10-16）\n\n"
        "Ariosto 人物、Lodoli《Apologhi》1787年印本及 Memmo 就任时的出版事件现分别登记为 person、archive、event KU；三个对象保持分开。正式关系仍留待 S6。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )

    if args.dry_run:
        print("S4 Ariosto and Lodoli batch dry-run passed:")
        for item in ITEMS:
            print(f"  {item['candidate']} ({item['type']}) -> {item['ku_id']}")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted paths unique")
        for cid, counts in direct.items():
            print(f"  {cid}: direct S2 statements={counts[0]}; relation candidates={counts[1]}")
        print(f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}")
        return 0

    for path, content in cards:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(ALIGNMENT, alignment_fields, planned_alignment)
    sync.write_csv(MANIFEST, manifest_fields, planned_manifest)
    accepted_lines = accepted.splitlines()
    for item in ITEMS:
        card_rel = item["card"]
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {card_rel}")
    ACCEPTED.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied S4 registration for 3 groups; manifest={len(planned_manifest):,}; pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
