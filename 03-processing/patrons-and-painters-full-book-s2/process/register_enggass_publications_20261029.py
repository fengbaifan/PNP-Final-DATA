from __future__ import annotations

import csv
import io
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
UNITS = ROOT / "04-knowledge" / "units"
PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
    "#s3-s4-s5-s6-enggass-publications-20261029"
)
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)


def card(title: str, name_en: str, chinese: str, english: str,
         body_quote: str, body_span: str, body_summary: str,
         note_quote: str, note_span: str, note_summary: str,
         bib_quote: str, bib_span: str, bib_summary: str,
         rows: list[tuple[str, str, str]], group: str, candidate: str) -> str:
    table_rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in rows)
    return f'''---
title: "{title}"
name_en: "{name_en}"
type: archive
evidence_status: source_backed
sources:
  - citation: "{HASKELL_CITATION}"
    location: "第20章，{body_span}"
    sentence_summary: "{body_summary}"
    original_quotes:
      - source_span: "{body_span}"
        text: >-
          {body_quote}
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/20_CHP-20Postscript.md
      source_span: "{body_span}"
  - citation: "{HASKELL_CITATION}"
    location: "第20章，{note_span}"
    sentence_summary: "{note_summary}"
    original_quotes:
      - source_span: "{note_span}"
        text: "{note_quote}"
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/20_CHP-20Postscript.md
      source_span: "{note_span}"
  - citation: "{HASKELL_CITATION}"
    location: "第21章书目，{bib_span}"
    sentence_summary: "{bib_summary}"
    original_quotes:
      - source_span: "{bib_span}"
        text: "{bib_quote}"
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/21_CHP-21Bibliography.md
      source_span: "{bib_span}"
created: '2026-10-29'
updated: '2026-10-29'
process_ref: {PROCESS_REF}
---

## 内容

### 描述

**中文：** {chinese}

**English:** {english}

### 文献身份与出版

| 字段 | 内容 | 依据 |
|---|---|---|
{table_rows}

## 关系与证据

### 关系记录

### 身份入口

- **S3身份组：** `{group}`；候选 `{candidate}` 映射至本KU。
- 题名、文献类型及出版资料据 Haskell 第21章书目；卡片仅记录该书的著录和第20章转述，未独立查阅该文献。
'''


cards = {
    "units/archives/enggass-painting-of-baciccio-1964": card(
        "《巴奇乔绘画》（The Painting of Baciccio）",
        "The Painting of Baciccio",
        "本卡标识 Robert Enggass 的《The Painting of Baciccio》。Haskell 第20章称该书为 Gaulli 专著，第21章书目列其题名、费城和1964年。中文题名为项目工作译名；该书未独立查阅，所述壁画研究不作本项目的独立核验结论。",
        "This unit identifies Robert Enggass's *The Painting of Baciccio*. Haskell calls it a monograph on Gaulli in chapter 20; the chapter 21 bibliography lists its title, Philadelphia, and 1964. The Chinese title is a working translation. The book has not been independently consulted, and Haskell's account of its fresco study is not presented as an independently verified finding.",
        "My account of Gaulli’s frescoes in the Gesù also needs to be supplemented (and sometimes corrected) by Robert Enggass’s important monograph on the artist which appeared at much the same time as the first edition of my book. Enggass’s study of the content of the frescoes is far more complete than my own, but he discusses their iconography essentially within the general context of the ‘church triumphant’ rather than in relation to those specific theological issues which (partly following Lanckoronska) I describe at some length.",
        "Markdown L43; printed p.399; PDF physical p.4",
        "Haskell称其对Gaulli及Gesù壁画的研究补充、有时修正本书叙述，并比较其图像解释语境。",
        "2 Enggass, 1964.",
        "Markdown L225; printed p.399 n.2; PDF physical p.4",
        "第20章第399页注2以作者姓氏和年份指向该书。",
        "Enggass, Robert: The Painting of Baciccio, Philadelphia 1964.",
        "Markdown L442; printed p.421; PDF physical p.11",
        "书目列出作者、题名、费城及1964年。",
        [
            ("原书所录题名", "The Painting of Baciccio", "S3"),
            ("文献类型", "专著；Haskell称为 monograph", "S1"),
            ("作者著录形式", "Enggass, Robert", "S3"),
            ("出版地", "Philadelphia", "S3"),
            ("出版年", "1964", "S3"),
            ("Haskell在本书中的描述", "称该专著补充并有时修正其对Gaulli在Gesù壁画的叙述；称Enggass对壁画内容的研究更完整，并将图像阐释置于“church triumphant”一般语境。", "S1"),
        ],
        "archive-group-ee153a1a2551", "cand-10929",
    ),
    "units/archives/enggass-altar-rail-st-ignatius-gesu-1974": card(
        "《罗马耶稣会堂圣依纳爵礼拜堂的圣坛栏杆》（The Altar-rail for St. Ignatius’ Chapel in the Gesù di Roma）",
        "The Altar-rail for St. Ignatius’ Chapel in the Gesù di Roma",
        "本卡标识 Robert Enggass 的期刊文章《The Altar-rail for St. Ignatius’ Chapel in the Gesù di Roma》。Haskell 第20章称其为讨论 Gesù 圣依纳爵祭坛的文章；注1为“Enggass, 1974”，第21章书目列出文章题名、期刊和页码。中文题名为项目工作译名；文章未独立查阅。",
        "This unit identifies Robert Enggass's journal article *The Altar-rail for St. Ignatius’ Chapel in the Gesù di Roma*. Haskell describes it in chapter 20 as an article on the altar of St Ignatius in the Gesù; note 1 reads “Enggass, 1974,” and the chapter 21 bibliography supplies the title, journal, and pages. The Chinese title is a working translation. The article has not been independently consulted.",
        "In addition to his monograph on Gaulli, Enggass has written an essential article on the altar of St Ignatius in the Gesù.",
        "Markdown L47; printed p.400; PDF physical p.5",
        "Haskell明确称Enggass写有一篇讨论Gesù圣依纳爵祭坛的文章。",
        "1 Enggass, 1974.",
        "Markdown L226; printed p.400 n.1; PDF physical p.5",
        "印本注1为“Enggass, 1974”；该短引与第21章同年且主题吻合的文章条目对应。",
        "Enggass, Robert: ‘The Altar-rail for St. Ignatius’ Chapel in the Gesù di Roma’ in Burlington Magazine, 1974, pp. 176-189.",
        "Markdown L443–444; printed p.421; PDF physical p.11",
        "书目列出文章完整题名、Burlington Magazine、1974年和第176–189页。",
        [
            ("原书所录题名", "The Altar-rail for St. Ignatius’ Chapel in the Gesù di Roma", "S3"),
            ("文献类型", "期刊文章", "S3"),
            ("作者著录形式", "Enggass, Robert", "S3"),
            ("期刊", "Burlington Magazine", "S3"),
            ("出版年", "1974", "S3"),
            ("文章页码", "176–189", "S3"),
            ("Haskell在本书中的描述", "称该文讨论Gesù圣依纳爵祭坛，并评价其为重要文章。", "S1"),
        ],
        "archive-group-99e635fcc4dd", "cand-10934",
    ),
    "units/archives/enggass-early-eighteenth-century-sculpture-rome-1976": card(
        "《罗马十八世纪早期雕塑——图文目录作品集》（Early Eighteenth-Century Sculpture in Rome—an illustrated catalogue raisonné）",
        "Early Eighteenth-Century Sculpture in Rome—an illustrated catalogue raisonné",
        "本卡标识 Robert Enggass 的《Early Eighteenth-Century Sculpture in Rome—an illustrated catalogue raisonné》。Haskell 第20章称该书增进了对 Gesù 堂内 Théodon 与 Legros 雕像及耶稣会赞助的认识；注2为“Enggass, 1976”，书目列其两卷本、费城和1976年。中文题名为项目工作译名；原书未独立查阅，未据此识别具体雕像。",
        "This unit identifies Robert Enggass's *Early Eighteenth-Century Sculpture in Rome—an illustrated catalogue raisonné*. Haskell says in chapter 20 that the book added to knowledge of statues by Théodon and Legros in the Gesù and of Jesuit patronage; note 2 reads “Enggass, 1976,” and the bibliography records two volumes, Philadelphia, and 1976. The Chinese title is a working translation. The book has not been independently consulted, and no individual statue is identified from this citation alone.",
        "In addition to his monograph on Gaulli, Enggass has written an essential article on the altar of St Ignatius in the Gesù, and in a book on eighteenth-century sculpture in Rome he has added to our knowledge of the statues by Théodon and Legros in the church—and thus to our knowledge of Jesuit patronage in general.",
        "Markdown L47; printed p.400; PDF physical p.5; S0 OCR ‘kra book’ checked against scan as ‘a book’",
        "Haskell称该书增进了对教堂内Théodon与Legros雕像及耶稣会赞助的认识。原Markdown的S0 OCR“kra book”据扫描校读为印本“a book”。",
        "2 Enggass, 1976.",
        "Markdown L226; printed p.400 n.2; PDF physical p.5",
        "印本注2为“Enggass, 1976”；与书目中的1976年两卷雕塑目录条目对应。",
        "Enggass, Robert: Early Eighteenth-Century Sculpture in Rome—an illustrated catalogue raisonné, 2 vols., Philadelphia 1976.",
        "Markdown L445; printed p.421; PDF physical p.11",
        "书目列出作者、题名、图文作品目录性质、两卷、费城和1976年。",
        [
            ("原书所录题名", "Early Eighteenth-Century Sculpture in Rome—an illustrated catalogue raisonné", "S3"),
            ("文献类型", "图文目录作品集（illustrated catalogue raisonné）", "S3"),
            ("作者著录形式", "Enggass, Robert", "S3"),
            ("卷册", "2 vols.", "S3"),
            ("出版地", "Philadelphia", "S3"),
            ("出版年", "1976", "S3"),
            ("Haskell在本书中的描述", "称该书增进了对Gesù堂内Théodon与Legros雕像及一般耶稣会赞助的认识；具体作品未识别。", "S1"),
        ],
        "archive-group-530040658564", "cand-10935",
    ),
}


def append_csv_rows(path: Path, rows: list[dict[str, str]]) -> None:
    existing = path.read_text(encoding="utf-8")
    lines = existing.splitlines()
    header = next(csv.reader([lines[0]]))
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=header, lineterminator="\n")
    for row in rows:
        writer.writerow(row)
    addition = out.getvalue()
    path.write_text(existing + ("" if existing.endswith("\n") else "\n") + addition, encoding="utf-8", newline="")


def patch_alignment() -> None:
    path = TABLES / "alignment.csv"
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    header = next(csv.reader([lines[0].rstrip("\r\n")]))
    changed: set[str] = set()
    replacements = {
        "cand-10929": ("units/archives/enggass-painting-of-baciccio-1964", "The S3 new group archive-group-ee153a1a2551 is registered from the p.399 citation and p.421 bibliography entry."),
        "cand-10934": ("units/archives/enggass-altar-rail-st-ignatius-gesu-1974", "The S3 new group archive-group-99e635fcc4dd is registered from p.400 note 1 and the p.421 bibliography entry."),
        "cand-10935": ("units/archives/enggass-early-eighteenth-century-sculpture-rome-1976", "The S3 new group archive-group-530040658564 is registered from p.400 note 2 and the p.421 bibliography entry."),
    }
    output = [lines[0]]
    for line in lines[1:]:
        ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        raw = line.rstrip("\r\n")
        values = next(csv.reader([raw]))
        record = dict(zip(header, values))
        candidate = record.get("candidate_id", "")
        if candidate in replacements:
            if candidate in changed or record.get("decision") != "new" or record.get("ku_id"):
                raise ValueError(f"unexpected existing alignment state for {candidate}")
            ku_id, note = replacements[candidate]
            record["ku_id"] = ku_id
            record["resolution_note"] += f" S4 registration: {ku_id}; {note}"
            out = io.StringIO(newline="")
            csv.DictWriter(out, fieldnames=header, lineterminator="").writerow(record)
            output.append(out.getvalue() + ending)
            changed.add(candidate)
        else:
            output.append(line)
    if changed != set(replacements):
        raise ValueError(f"alignment rows changed: {sorted(changed)}")
    path.write_text("".join(output), encoding="utf-8", newline="")


def main() -> None:
    manifest = TABLES / "ku-manifest.csv"
    accepted = ROOT / "04-knowledge" / "accepted.yml"
    relations = TABLES / "relations.csv"
    if any((UNITS / (key.removeprefix("units/") + ".md")).exists() for key in cards):
        raise FileExistsError("one or more target archive cards already exist")
    for path in (manifest, accepted, relations):
        data = path.read_text(encoding="utf-8")
        if any(ku_id in data for ku_id in cards):
            raise ValueError(f"target KU already appears in {path}")

    for ku_id, text in cards.items():
        card_path = UNITS / (ku_id.removeprefix("units/") + ".md")
        card_path.parent.mkdir(parents=True, exist_ok=True)
        card_path.write_text(text, encoding="utf-8", newline="\n")

    manifest_rows = [
        {"ku_id": ku_id, "type": "archive", "canonical_name": text.splitlines()[1].split('"')[1].split("（")[0],
         "name_en": text.splitlines()[2].split('"')[1], "source_task": "patrons-and-painters-full-book-s2",
         "card_path": f"04-knowledge/units/{ku_id.removeprefix('units/')}.md"}
        for ku_id, text in cards.items()
    ]
    append_csv_rows(manifest, manifest_rows)

    accepted_text = accepted.read_text(encoding="utf-8")
    marker = "claims:\n"
    if marker not in accepted_text:
        raise ValueError("accepted.yml has no claims boundary")
    accepted_lines = "".join(f"- 04-knowledge/units/{ku_id.removeprefix('units/')}.md\n" for ku_id in cards)
    accepted.write_text(accepted_text.replace(marker, accepted_lines + marker, 1), encoding="utf-8", newline="")

    patch_alignment()

    relation_rows = [
        {"relation_id": "rel-2577", "subject_ku_id": "units/archives/enggass-painting-of-baciccio-1964", "object_ku_id": "units/persons/robert-enggass", "predicate": "authored_by", "time": "", "role": "作者", "scope": "仅记录Haskell书内对1964年专著作者的归属", "origin": "book", "status": "formal", "source_id": "haskell-1980-rev-ed", "source_span": "Markdown L43; printed p.399; note 2 L225; bibliography L442, printed p.421", "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md", "note": "statement=st-chp20-p399-enggass-monograph-and-fresco-content; bibliography_statement=st-chp21-bib-l420-459-entry-18; the work itself was not independently consulted."},
        {"relation_id": "rel-2578", "subject_ku_id": "units/archives/enggass-altar-rail-st-ignatius-gesu-1974", "object_ku_id": "units/persons/robert-enggass", "predicate": "authored_by", "time": "", "role": "作者", "scope": "仅记录Haskell书内对1974年期刊文章作者的归属", "origin": "book", "status": "formal", "source_id": "haskell-1980-rev-ed", "source_span": "Markdown L47; printed p.400; note 1 L226; bibliography L443–444, printed p.421", "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md", "note": "statement=st-chp20-p400-enggass-jesuit-altar-article; bibliography_statement=st-chp21-bib-l420-459-entry-19; the article itself was not independently consulted."},
        {"relation_id": "rel-2579", "subject_ku_id": "units/archives/enggass-early-eighteenth-century-sculpture-rome-1976", "object_ku_id": "units/persons/robert-enggass", "predicate": "authored_by", "time": "", "role": "作者", "scope": "仅记录Haskell书内对1976年两卷目录作者的归属", "origin": "book", "status": "formal", "source_id": "haskell-1980-rev-ed", "source_span": "Markdown L47; printed p.400; note 2 L226; bibliography L445, printed p.421", "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md", "note": "statement=st-chp20-p400-enggass-rome-sculpture-book; bibliography_statement=st-chp21-bib-l420-459-entry-20; the book and cited statues were not independently consulted or identified."},
    ]
    current_relations = list(csv.DictReader(relations.open(encoding="utf-8", newline="")))
    expected_next = max(int(row["relation_id"].split("-")[1]) for row in current_relations) + 1
    if expected_next != 2577:
        raise ValueError(f"unexpected next relation id: {expected_next}")
    append_csv_rows(relations, relation_rows)
    print(f"registered {len(cards)} archive cards, 3 S4 mappings, and {len(relation_rows)} authored_by edges")


if __name__ == "__main__":
    main()
